# fx2-cmix transformer — C++ AVX2 single-thread inference SPEC

This document is the single source of truth for the C++ implementation of the
transformer whose outputs `training_recipes/save_outputs.py` saves. Every
subagent working on this project must follow it exactly. If you discover that
something here contradicts the Python code, the Python code wins — fix this file
and note it in your report.

## 0. Goal and constraints

- Single-threaded AVX2 (Zen 2, EPYC 7702) streaming inference, batch size 1.
- Interface: consume a stream of (token, prior distribution over 205) pairs,
  after each pair output the probability distribution over the *next* token,
  without having seen that token.
- Loss degradation vs the Python implementation must be ≤ 0.1% relative
  (target: ~0.01% or less). Loss = mean over predicted tokens of -log p[target].
- Maximize throughput (tokens/s). L3 footprint is a secondary objective.
- The model: `models/6m-q4-fp32.tch`, config in `training_recipes/save_outputs.py`.

## 1. Model architecture (config values are fixed constants)

- vocabulary_size V = 205, d_model D = 192, n_layers = 12, d_mlp = 768
- Layers 0..11. kimi_linear = [T,T,T,F, T,T,T,F, T,T,T,F]:
  layers 3, 7, 11 are **vanilla sliding-window attention**, the other 9 are
  **Kimi linear attention (KDA)**.
- Vanilla attention: 3 query heads, 3 kv heads, d_head 64 (no GQA), window_size
  1024, rope_base 10000, query_key_norm true, attention scale = 1/sqrt(64) = 0.125.
  The window is the one config value that is a *build parameter* of the C++
  engine: `-DATTN_WIN=<W>` (default 1024, `src/attn_window.h`) sizes the KV
  rings, scratch buffers and the var/fixed kernel switch, and the loaders
  reject a weights file whose `config.ints[6]` differs from the compiled-in
  W. A checkpoint trained with another window is exported with
  `FX2_WINDOW=<W>` on the Python side (`work/sota/train/modal_train.py::export
  --window W`) and run with a `-DATTN_WIN=W` build. Everything below is
  written for W=1024.
  **Per-layer windows (2026-09-19):** a checkpoint trained with
  `train_lex.py --window-mults m0,m1,m2` (pysrc/model.py
  `TransformerConfig.window_size_multipliers`, one entry per vanilla layer in
  layer order, e.g. `1,1,2` = layers 3 and 7 at W, layer 11 at 2W) runs
  vanilla layer vi at window `W * m_vi`. Build with `-DATTN_WIN_MULTS=m0,m1,m2`
  (`src/attn_window.h`: `attn_win::win(vi)`; default `1` = every layer at W;
  the lext_big build knob is `TF_WINDOW_MULTS`), export with
  `FX2_WINDOW_MULTS=m0,m1,m2` (`modal_train.py::export --window-mults`), which
  writes `config.window_mults` int32[NV] (section 4; absent = all 1). The
  loaders refuse a file whose multipliers differ from the build. Each layer's
  KV ring, ring slot (`t % W_vi`), var/fixed kernel switch (`t+1 < W_vi`) and
  scratch sizing follow its own window (`src/opt/attn.cpp attn_layer_*`);
  RoPE is indexed by the absolute position and does not depend on the window.
- KDA: 3 heads, d_head 64, convolution kernel size 4.
- MLP: 192 -> 768, relu², 768 -> 192.
- No weight sharing (each layer has its own weights). No dropout, model in eval.
- skip_connections true, token_embedding_connections true, prior_embedding true,
  embedding_norm true, prior_embedding_norm true, logit_softcap 15.0.
- prior_logit_mixing false, prior_embedding_on_logprobs false → the priors enter
  ONLY through the prior embedding; `prior_logprob_cap` is unused.

## 2. Quantization semantics (exact)

There are two kinds of quantizers; both are "fake quantization" in Python: the
quantized-int times scale product is what enters the fp32 arithmetic. All
scales are learned Parameters stored fp32 in the checkpoint, but **rounded to
bfloat16 (round-to-nearest-even) before use**; arithmetic is fp32.

Quantize(x) for a block with scale parameter s_fp32:
```
s   = fp32(bf16(s_fp32))              # bf16 rounding, then exact fp32
q   = clamp(round_half_even(x / s), qmin, qmax)   # fp32 IEEE division!
xq  = q * s                           # dequantized value used by Python
```
- Weights: buckets 15 → q ∈ [-7, 7] (int4 symmetric). Block = one row of the
  weight matrix, i.e. per-output-channel scale, shape (d_out,).
  **Scales can be negative** (e.g. blocks 3/7 q/k projections) — do not assume
  positivity for weights.
- Activations: buckets 256 → q ∈ [-128, 127]. Block = the whole feature vector:
  ONE static scalar scale per quantizer site (NOT per token — the scale is a
  trained constant). All activation scales in this checkpoint are positive.
- q/k/v post-rope quantizers in vanilla attention: one scale PER HEAD,
  shape (3,), q ∈ [-128,127].

A `CastedLinear` with MatmulQuantization does:
```
xq = fake_quant_act(x)      # per-site static scalar scale s_x
wq = fake_quant_weight(w)   # per-row scale s_w[o]
y[o] = sum_i xq[i] * wq[o,i]        (fp32 dot in Python)
     = s_x * s_w[o] * sum_i qx[i] * qw[o,i]   (C++: exact int32 dot, then one fp32 multiply
                                               — compute (s_x*s_w[o]) per row; do
                                               float(s_x*s_w[o]) * float(int_dot); tiny (~1e-7)
                                               reassociation difference vs Python is acceptable)
```
No biases anywhere in this model.

In C++, weights are stored pre-quantized (ints + scales from the weights file);
activation quantization happens at runtime: `q = clamp(round_half_even(x / s), -128, 127)`
using IEEE fp32 division (`_mm256_div_ps`) and `_mm256_round_ps(..., _MM_FROUND_TO_NEAREST_INT)`
to match torch bit-for-bit, then the integer matmul.

Quantized matmul list (all int8-activation × int4-weight), per token:
| name | shape (out×in) | count | notes |
|---|---|---|---|
| prior_embedding | 192×205 | 1 | input = quantized prior probs, very sparse (~15 nonzero of 205, sometimes dense) |
| kimi q/k/v proj | 192×192 | 3×9 | |
| kimi out proj | 192×192 | 1×9 | |
| kimi forget up / out-gate up | 64×192 | 2×9 | |
| kimi forget down / out-gate down | 192×64 | 2×9 | |
| vanilla q/k/v/o proj | 192×192 | 4×3 | |
| mlp up | 768×192 | 12 | |
| mlp down | 192×768 | 12 | input ≥ 0 after relu² → int8 in [0,127], unsigned×signed vpmaddubsw works directly |
| unembedding | 205×192 | 1 | |

Total ≈ 5.83 M MAC/token; int4-packed weight bytes ≈ 2.92 MB/token streamed.

NOT quantized (pure fp32 matvecs): kimi conv (192×4 per-channel), kimi
beta_projection (3×192).

### 2a. Dynamic per-token activation scales (build option `-DTF_ACTQ_DYN=1`, 2026-09-19)

A checkpoint trained with `work/sota/train/train_lex.py --actq-dynamic-mm` (pysrc/quantization.py
`Quantization.dynamic=True`) has NO learned activation scales on the matmul inputs. Every
`CastedLinear` with a `MatmulQuantization` — kimi q/k/v projections, forget/output gate up AND down
(the 64-dim intermediate is quantized dynamically too), kimi out-proj, vanilla q/k/v projections,
attention out-proj, mlp up (input xn) and mlp down (input relu²), prior_embedding (the 205 prior
probs), unembedding — quantizes each token's input vector v[0..n) with its own scale:
```
s    = max(max_i |v[i]|, 1e-12) / 127.0            # fp32: torch clamp(min=1e-12), IEEE division by qmax
q[i] = clamp(round_half_even(v[i] / s), -128, 127)  # IEEE fp32 division, as in section 2
xq   = q * s                                        # dequantized value used by Python
```
`quantize_queries/keys/values` (post-rope q/k/v of the vanilla attention, int8 KV ring) keep their
learned static per-head scales. An all-zero vector gives s = 1e-12/127 and q = 0 everywhere.

C++ semantics (both engines, bit-identical to each other): the arena/QLinear fold holds the WEIGHT
row scale only (× codebook grid), and the matmul output is
```
y[o] = (fold[o] * float(int_dot[o])) * s            # two separately rounded fp32 multiplies (no FMA, no
                                                    #  reassociation: kernels.cpp qmatvec then scale_vec;
                                                    #  opt: qmat_dense.h (e)-(h), qmat_sparse.h *s kernels)
```
then the consumer proceeds as in the static model (residual `+=` as a separate add; relu² on the
scaled y; the relu² vector and the gate intermediates get their own dynamic scale before their
matmul). The kimi layer's five projections and the vanilla layer's three share ONE quantized copy of
xn (identical input ⇒ identical q). The reassociation difference vs Python's fp32 `linear` on the
dequantized values is the same ~1e-7 as in section 2.

Weights file: `pysrc/export_weights.py` with `FX2_ACTQ_DYNAMIC_MM=1` exports NO
`*.quantize_activation.scale` tensors (the checkpoint holds all-zero buffers) and adds
`config.actq_dynamic_mm` int32[1] = 1 (section 4). The loaders (`arena_build.cpp`, `model.cpp`) treat
an absent tensor as 0 and refuse a file whose flag differs from the binary's `TF_ACTQ_DYN`
(`src/opt/tf_arch.h`; lext_big build knob `TF_ACTQ_DYN=1`).

### 2b. AVX-512 VNNI fast path (build option `-DTF_AVX512=1`, 2026-09-19)

The matmul kernels exist in two implementations with BIT-IDENTICAL outputs: the AVX2 kernels
(`src/opt/qmat_dense.cpp`, `qmat_sparse.cpp`; the default and the only code in a `TF_AVX512=0` build)
and their AVX-512 twins (`src/opt/qmat_dense_avx512.cpp`, `qmat_sparse_avx512.cpp`, declared in
`qmat_avx512.h`, namespace `fx2::opt::avx512`). The two TUs are the only objects compiled with
`-mavx512f -mavx512bw -mavx512vl -mavx512vnni` (exactly the Tiger Lake ∩ Zen 4 subset; NOT
`-march=x86-64-v4`, which lacks VNNI); everything else stays x86-64-v3. `qmat_cpu.cpp`
(`cpu_has_avx512_vnni()`, cpuid leaf 7 + XCR0 opmask/ZMM state, `FX2_FORCE_AVX2=1` override, always
false in a `TF_AVX512=0` build) decides ONCE at load (`OptModel::avx512`) which path a process runs:

| site | AVX2 host (and every `TF_AVX512=0` binary) | AVX-512 host |
|---|---|---|
| 192-in dense: kimi/vanilla q/k/v, out-proj, gate up (64×192), mlp up (768×192), unembedding (non-W8) | `QDense` unpacked int8 arena, `qgemv_*` (vpmaddubsw) | `QPackedCB` packed int4 + LUT arena (qmat.h section 4, half the bytes), `avx512::qgemv_pcb_*` (vpshufb LUT + vpdpbusd) |
| 64-in dense: gate down (192×64) | `QDense`, `qgemv_f32[s]` | same `QDense` arena, `avx512::qgemv_f32[s]` |
| mlp down / prior: `QSparse4` int4 columns | `qsparse4_*` | same arena, `avx512::qsparse4_*` (16 int32 accumulators hold all 192 rows, no int16 flush) |
| prior / unembedding at 8 bits (`QMAT_SMALL_W8`) | `qw8_f32` | same tables, `avx512::qw8_f32` |
| KDA, attention, glue, norms, head | AVX2 | AVX2 (not dispatched) |

Why the bits are identical: every int32 dot is an exact integer on both paths (vpdpbusd accumulates
u8·s8 groups of four straight into int32; the AVX2 int16 stage never saturates by construction —
`QMAT_WIDEN_CHUNKS` / `QMAT_FLUSH_PAIRS`), so the summation order is irrelevant; the fp32 epilogues
are the same op sequences (cvtepi32_ps, mul, [mul s], [add]; never fused) and the phase-2 quantizers
are verbatim copies; corr/fold/activation conventions of the packed arena are those of `QDense`
(pad rows/columns use LUT entry 15 = weight 0, so no assumption on the codebook's levels). Verified
by `src/opt/test_avx512` (every entry point vs its AVX2 twin and the scalar int64 reference on random
and extreme inputs, plain and codebook+W8 builds), by `test_e2e_opt --no-ref` digests with and without
`FX2_FORCE_AVX2=1`, and by AMD↔Intel compressor round trips. The dispatch lives in `model_opt.cpp`
(`mm_*` / `sp4_*` helpers: one perfectly predicted branch per matmul); `arena_build.cpp` builds
`QSite::pm` instead of `QSite::m` for the 192-in sites on an AVX-512 host. `FX2_VERBOSE_ISA=1` prints
the chosen path at load. Neither the weights file nor the archive format depends on the path.

## 3. Exact math of every component

### 3.1 rms_norm (used everywhere, no learnable weight except noted)
```
rms_norm(x)[i] = x[i] / sqrt(mean_j(x[j]^2) + 1.1920928955078125e-07)   # eps = FLT_EPSILON
```
Applied over: d_model=192 (block inputs, embedding norms, final norm), d_head=64
(q/k per head in vanilla attention). Compute in fp32. (torch may differ by ~1 ulp
in the reduction; irrelevant.)

### 3.2 Embedding path (start of article position t input token c, prior p[205])
```
tok = rms_norm(dequant_embedding_row(c))     # embedding weight int4-quantized per row
pri = rms_norm(prior_linear(fake_quant(p)))  # 192×205 quantized matmul on prior probs
x = tok + pri
```
- Prior input p = fp32 of the float16 prior row, elements ≥ 0; quantization
  clamps round(p/s) to 127 (p/s can reach ~360). ~15 nonzeros on average.
- `tok` depends only on c → precompute a 205×192 fp32 table of NORMED embedding
  rows at load. The UN-normed embedding rows are NOT needed at runtime.
- token_embeddings (the normed rows) are also reused by every block (§3.3).

### 3.3 Block wiring (layer ℓ = 0..11)
```
# token-embedding connection (constants, fp32 scalars from checkpoint):
x = residual_stream_coefficient[ℓ] * x + token_embedding_coefficient[ℓ] * tok

# skip connections: sources are layers 0..5 (x AFTER the block finishes),
# destinations 6..11 added BEFORE the block body runs (before the attn norm below,
# but AFTER the token-embedding connection above? NO — order in Python:
#   1. skip-add happens at the top of the layer loop: x += skip_w[i]*skip  (dest layers)
#   2. then Block.forward: token-embedding connection, attention, mlp
# Pairing: layer 6 gets output of layer 5, 7←4, 8←3, 9←2, 10←1, 11←0 (stack pop).
# skip_w index: i = layer - 6.

x = x + attention(rms_norm(x))     # vanilla or KDA depending on layer
x = x + mlp(rms_norm(x))
```
After layer 11: `x = rms_norm(x)`, then unembedding → logits.

### 3.4 MLP
```
h = up(fake_quant(xn))          # 768, int matmul, dequant to fp32
h = relu(h)^2                   # fp32
y = down(fake_quant(h))         # 192; h ≥ 0 → unsigned int8 in [0,127]
```

### 3.5 Vanilla attention (layers 3, 7, 11), window W=1024 (= ATTN_WIN × the layer's ATTN_WIN_MULTS entry, build parameters; see section 1)
```
xn = rms_norm(x)
q = Q(fake_quant_q(xn)) ; k = K(fake_quant_k(xn)) ; v = V(fake_quant_v(xn))   # each 192, separate act scales
q,k,v viewed as 3 heads × 64
q = rms_norm_per_head(q); k = rms_norm_per_head(k)      # eps FLT_EPSILON, over 64
q = rope(q, pos); k = rope(k, pos)                       # §3.6
q = fake_quant_per_head(q)  → int8 ints qq[h][64], scale sq[h]
k = fake_quant_per_head(k)  → int8 ints qk[h][64], scale sk[h]
v = fake_quant_per_head(v)  → int8 ints qv[h][64], scale sv[h]
# attention over keys j ∈ [max(0, t-(W_vi-1)), t] of the SAME article (W_vi = this layer's window, 1024 below):
score[h][j] = 0.125 * sq[h]*sk[h] * (qq[h]·qk[h,j])       # int32 exact dot × fp32 scale
p = softmax_fp32(score[h][:])                             # exp(s - max)/Σ
out[h] = Σ_j p[j] * (sv[h] * qv[h,j][:])                  # fp32 accumulation
y = O(fake_quant_o(concat(out)))                          # output projection, int matmul
```
- KV cache: store qk, qv (int8, 192 B each) per position, ring buffer of W_vi
  slots (1024 at the base window; per-layer sizes with ATTN_WIN_MULTS).
- Python computes attention in fp32 on the dequantized values (flex_attention);
  C++ integer QK dot × scales is the same sum re-associated; PV in fp32.
- Two kernels: t+1 < W (variable length, growing) and t+1 ≥ W (fixed 1024 shape).
- Optional (default ON, must be toggleable to measure): skip exp+PV for
  positions with score - max < -21 (e^-21·1024 < 9e-7 relative effect). The
  softmax denominator must still include ALL positions' exp values? NO — it may
  exclude the skipped ones (their total mass < 1e-6 of the max term alone;
  measured effect on loss must be reported by the correctness test with the
  toggle on and off; keep OFF if it degrades loss > 0.005%).

### 3.6 RoPE (vanilla attention only)
```
inv_freq[i] = 1 / (10000 ** linspace(0,1,32)[i]) = 10000^(-i/31), i = 0..31   # NOTE: /31, endpoint inclusive
angle = position * inv_freq[i]      # fp32 multiply of fp32(position) × fp32 inv_freq
c = cos(angle), s = sin(angle)      # fp32
head pairs (x0, x1) = (x[2i], x[2i+1]):
y[2i]   =  x0*c + x1*s
y[2i+1] = -x0*s + x1*c
```
- `position` is the GLOBAL position within the reference micro-batch during
  testing (per-article offset provided from the export), and the position
  within the article (0-based) in production. The API takes an optional
  rope-position offset per article; default 0.
- inv_freq values are exported from Python in the weights file (exact fp32).
- Precompute at load a sin/cos table for positions 0..max_len-1 (fp32, using
  libm sinf/cosf on the fp32 angle — matches torch within ~1 ulp; the export
  also ships torch's own sin/cos table for positions < 131072 — USE THE SHIPPED
  TABLE to eliminate even that divergence; beyond 131072 compute with sinf).
  (Table read = 256 B/token, negligible bandwidth; don't keep it hot in cache.)

### 3.7 Kimi linear attention (KDA) — exact semantics in KIMI_SEMANTICS.md
Summary (validated against fla 0.5.1 chunk_kda with use_qk_l2norm_in_kernel=True,
use_gate_in_kernel=True; the per-step recurrent form):
```
xn = rms_norm(x)
q = Qp(fake_quant(xn)); k = Kp(fake_quant(xn)); v = Vp(fake_quant(xn))      # 192 each
q = conv_silu_q(q); k = conv_silu_k(k); v = conv_silu_v(v)                  # §3.8, per-channel causal conv k=4 + silu, fp32
g_raw = ForgetDown(fake_quant(ForgetUp(fake_quant(xn))))                    # 192, low-rank int matmuls (no nonlinearity between)
beta[h] = sigmoid(beta_proj(xn))                                            # 3, unquantized fp32 matvec on xn
og  = OutGateDown(fake_quant(OutGateUp(fake_quant(xn))))                    # 192
per head h (d=64), state S[h] ∈ R^{64(k)×64(v)}, init 0 at article start:
  qn = l2norm(q[h]); kn = l2norm(k[h])                # exact eps in KIMI_SEMANTICS.md
  g[h][i] = -exp(A_log[h]) * softplus(g_raw[h][i] + dt_bias[h][i])   # per-channel log-decay (exact fn in KIMI_SEMANTICS.md)
  decay = exp(g[h])                                    # 64 values (k-dim)
  S = diag(decay) @ S                                  # per-k-row decay
  r = S^T kn        (64, v-dim)                        # k^T S
  S += outer(kn, beta[h] * (v[h] - r))                 # delta rule
  o[h] = S^T (0.125 * qn)     (64)                     # scale = 64^-0.5 (chunk_kda default; q side only)
o = FusedRMSNormGated(o, og): per head: rms_norm_64(o[h]) * norm_weight * sigmoid(og[h])   # exact form/eps in KIMI_SEMANTICS.md
y = OutProj(fake_quant(concat(o)))
```
(The exact order of decay/delta operations, eps values, softplus form, and the
gated-norm formula MUST be taken from KIMI_SEMANTICS.md, which is validated
numerically against the Triton kernels. The above is the intended shape.)

### 3.8 Causal conv + SiLU (kimi q/k/v, per channel c, kernel size 4)
```
y[t][c] = silu( Σ_{i=0..3} w[c][i] * x[t-3+i][c] )     # x[<article start] = 0
silu(z) = z * sigmoid(z) = z / (1 + e^-z)
```
Keep a 3-deep history per channel per conv (or one 192×4 ring) per layer.

### 3.9 Head: unembedding, softcap, softmax
```
xn = rms_norm(x)                       # final norm
l = Unembed(fake_quant(xn))            # 205 logits
l = 15 * tanh(l / 15)                  # logit softcap, fp32 tanh
prob = softmax_fp32(l)                 # exp(l - max) / Σ
```
Output: 205 fp32 probabilities (also a helper to write f16 like the reference file).

## 4. Weights file format (written by pysrc/export_weights.py)

Binary little-endian file `cpp_infer/data/weights.bin`:
```
magic "FX2TFW01" (8 bytes)
u32 n_tensors
repeat n_tensors:
  u32 name_len, name bytes (no NUL)
  u8  dtype: 0 = int8, 1 = uint16 (raw bf16 bits), 2 = float32, 3 = int32
  u32 ndim, u32 shape[ndim]   # row-major, same orientation as the torch tensor
  data (packed, row-major)
```
Tensor list (names = torch state-dict names with suffixes):
- For every quantized weight `X.weight`: `X.weight.q` int8 (values in [-7,7],
  same shape as torch weight, quantized EXACTLY as QuantizeFunction:
  bf16-rounded scale, fp32 division, round-half-even, clamp) and
  `X.weight.scale` uint16 bf16 bits, shape (d_out,).
- For every activation quantizer `Y.quantize_activation.scale` (and
  `quantize_queries/keys/values.scale`): `Y...scale` uint16 bf16 bits (the value
  actually used in arithmetic).
- Unquantized tensors raw float32 under their state-dict names: conv weights
  (192×4), beta_projection.weight (3×192), dt_bias (192), log_baseline_decay_rate (3),
  output_fused_norm_gate.weight (64), residual/token coefficients (1), 
  skip_connection_weights.value (6).
- Extra: `rope.inv_freq` f32[32] (computed by torch exactly as in make_rope_args);
  `rope.sin` / `rope.cos` f32[131072×32] torch fp32 tables (matches training exactly).
  (rope.sin/cos make the file ~34 MB bigger; that is fine.)
- Extra: `config.ints` int32[...] = {205, 192, 12, 64, 3, 768, 1024, 64, 3, 4, 10000}
  and `config.kimi` int32[12] = the kimi_linear flags.
- Optional extras (absent = the shipped recipe): `config.codebook_grid` f32[1] + `config.codebook_max_int`
  int32[1] + one `X.weight.codebook` int8[15] per codebook weight (FX2_WCODEBOOK=1, src/opt/qmat.h);
  `config.actq_dynamic_mm` int32[1] = 1 when the activation scales are dynamic per token (section 2a;
  then no `*.quantize_activation.scale` tensors are present, the `quantize_queries/keys/values.scale`
  tensors still are); `config.window_mults` int32[NV] (NV = number of vanilla-attention layers, one
  multiplier per vanilla layer in layer order) when the checkpoint uses per-layer attention windows
  `config.ints[6] * config.window_mults[vi]` (FX2_WINDOW_MULTS, section 1; written only when some
  multiplier differs from 1, so a uniform-window export is byte-identical to the pre-2026-09-19 file).

The C++ loader may repack layouts arbitrarily at load time (pack nibbles,
transpose, reorder rows, precompute per-row 128·Σw corrections, fold scales,
etc.). The FILE stays simple/natural.

Compressed containers (COMPRESSION.md; `pysrc/weights_compress.py` writes,
`src/weights_io_compressed.cpp` reads, `bin/test_weights_compressed` proves the
tensors bit-identical to this file): `FX2TFWC1` (uniform-1/15 range-coded int4),
`FX2TFWC2` (one adaptive-binary range-coded stream, rope tables recomputed),
`FX2TFWC3` (2026-09-19: v2 with the int8 payloads coded by per-tensor adaptive
frequency counts, −28 KB per copy). The shipped `.tfwc2` files may hold any of
the three; every loader dispatches on the 8-byte magic.

## 5. Test data (written by pysrc/export_testdata.py) — cpp_infer/data/

- `test_tokens.u8`, `test_bounds.i32`: copies of data/tokens-1024-articles.uint8
  and data/article-boundaries-1024-articles.int32 (1024 articles, 2,323,337 tokens).
- `test_priors.f16`: for each selected article, the ppmd prior rows for its
  token range concatenated in the same order as test_tokens (one 205-f16 row
  per token; the row of the article-final token is included for alignment but
  unused as input... actually every token's row IS used as input at its
  position; the final token of an article is simply never fed as input).
  Row r of test_priors is the prior paired with input token r (data.py pairs
  input token at global index g with priors row g).
- `test_rope_offsets.i32`: 1024 entries — the article's start position within
  its packed reference micro-batch (micro_batch_tokens=131072, greedy packing
  by (len-1) in selected order, trailing batch kept). Article i (subset order)
  contributed positions [off, off+len_i-1) of its micro-batch.
- `test_ref_probs.f16`: symlink/copy of data/transformer-probs-1024-articles.bfloat16
  (float16 despite the name). Row semantics: row r = distribution over token
  r+1; the LAST row of each article contains the ppmd prior → EXCLUDED from
  comparison and from loss.
- `ref_loss.txt`: two lines, full-precision decimal text:
  `fp32 <loss_sum> <count> <mean>` (exact fp32 reference loss from rerunning
  the Python model on GPU over the reference micro-batches) and
  `f16 <loss_sum> <count> <mean>` (recomputed from the f16 file with
  -log(max(p, 1e-12)) for sanity). count = 2,322,313 predicted tokens.
- `dumps/`: 3 diagnostic articles, subset indices K = 0 (274 tokens), 4 (2083
  tokens), 22 (18593 tokens — covers the t=1024 window transition; rope offset
  44481). For each, fp32 .npy dumps of per-component intermediates for the
  first min(len-1, 4096) positions of the article, captured from its packed
  reference micro-batch (batch dim removed: position is the first axis).
  Files `dumps/article{K}/{NN}_{component}.npy` + `meta.json` (orig article
  id, length, rope_offset, micro_batch_index, dumped position count, the
  micro-batch's article list). Components (NN = layer 00..11, 12 = head):
  `00_x0` (embedding sum = input to block 0); per layer: `block_input`
  (after the skip add, before the residual/token-embedding coefficients),
  `attn_out` (y added to the residual), `mlp_out`, `block_output`; kimi
  layers: `kimi_conv_q/k/v` (post conv+silu), `kimi_g_raw` (forget-gate
  low-rank output, pre dt_bias/softplus), `kimi_beta_raw` (pre-sigmoid,
  (N,3)), `kimi_out_gate`, `kimi_kda_out` (raw chunk_kda output, (N,3,64)),
  `kimi_gate_in` (gate as passed to the fused norm), `kimi_gated_norm_out`;
  vanilla layers: `attn_q/k/v_quant` (fake-quantized fp32 post-rope,
  (N,3,64)), `attn_q/k/v_int8` (the same as int8 ints; range [-128,127]),
  `attn_pre_oproj` (concat attention out, input of the output projection);
  head: `12_final_norm`, `12_logits` (post-softcap), `12_probabilities`
  (fp32 softmax; its f16 rounding equals the test_ref_probs rows).
  `dumps/stats.json` holds the losses, the probability-recomputation result,
  prior/mlp sparsity and residual max-abs diagnostics.

## 6. C++ deliverables (cpp_infer/)

- `weights_io.{h,cpp}`: file loader.
- `model.{h,cpp}` (+ kernels): the transformer. Public interface:
  ```cpp
  struct Transformer {
    explicit Transformer(const char* weights_path);
    void begin_article(int64_t rope_position_offset = 0);  // resets KV/KDA/conv state
    // feed token t and its prior (205 f16 values); fills probs[205] (fp32,
    // distribution over the NEXT token). Also float-prior overload.
    void step(uint8_t token, const uint16_t* prior_f16, float* probs_out);
  };
  ```
- `test_components`: binary comparing every dumped component (max-abs and
  max-rel divergence per component; fails loudly on > 1e-3 rel for fp32 paths).
- `test_e2e`: runs all 1024 articles, computes loss, compares with ref_loss.txt
  and reports relative degradation; also max/mean per-row L1 distance of
  probability vectors vs test_ref_probs.f16 (excluding article-final rows).
  MUST print the verdict vs the 0.1% budget. Also supports running a subset of
  articles (--articles N) for quick iteration.
- `bench`: throughput benchmark over the test set (tokens/s, cycles/token),
  with `--profile` per-part breakdown (rdtsc instrumentation; compiled in but
  runtime-toggled; report both instrumented and clean throughput).
- `Makefile`: g++-13 AND clang++-17 targets, `-O3 -march=znver2` (NO -ffast-math;
  `-fno-math-errno` is allowed), `-static` not required. `-DTF_AVX512=1` in CXXFLAGS adds the
  runtime-dispatched AVX-512 VNNI kernel objects (section 2b); `src/opt/Makefile test_avx512`
  builds their bitwise equality test.
- Style: plain C++17, no external deps beyond libc/libm/immintrin.

## 7. Reference batching details (for exact reproduction)

The reference run packed the 1024 selected articles (in `selected` order =
subset file order) into micro-batches of up to 131072 positions, each article
contributing (len-1) positions; when an article would overflow, the batch is
flushed. Positions within the batch are consecutive across articles. RoPE used
GLOBAL batch positions. Attention/KDA/conv reset at article boundaries
(document masking), so apart from RoPE offsets articles are independent.
Padding rows (token 0, prior 0) after the last article of a batch do not affect
earlier articles (causal).

The loss over predicted tokens (this is THE number for the 0.1% criterion):
for each article, positions 0..len-2 predict tokens 1..len-1;
loss = -Σ log softmax(logits)[target] / count, count = Σ (len_i - 1) = 2,322,313.

## 8. Performance notes (initial analysis, refine with MACHINE.md)

- EPYC 7702 Zen 2: 2 × 256-bit FMA + 2 × 256-bit int-ALU-ish pipes; vpmaddubsw
  and vpmaddwd 2/cycle (FP0/FP1), vpaddw/vpand etc on other pipes; 2 loads/cycle
  (≤ 32 B each); L1 32 KB, L2 512 KB, L3 16 MB per CCX (4 cores). Max clock
  reported 2.18 GHz (MEASURE the actual sustained clock; all cycle math must use
  the measured value).
- Weights stream L3→core every token (≈2.92 MB packed int4): expect the int4
  matmuls to be simultaneously near compute- and near L3-bandwidth-bound; this
  is why packing (int4 nibbles, unpack in-register) vs unpacked (int8 bytes) is
  a real tradeoff to be decided by measurement.
- int8 dot trick: vpmaddubsw(u8, s8) with u8 = x+128 (activations biased) and
  s8 = weight nibble in [-7,7]; accumulate up to 8 vpmaddubsw results in int16
  (max |sum| = 8·2·255·7 = 28,560 < 32,767 — safe); then vpmaddwd(acc, 1) into
  int32. Correct at the end: dot -= 128 · Σ_row(qw) (precomputed per row at load).
  For mlp down the activations are already unsigned ([0,127]) — no bias/correction.
- Layout weights contiguously in exact consumption order (one big arena) so the
  L2/L3 hardware prefetchers see pure sequential streams; add software prefetch
  where measured to help.
- KV cache int8 (192 B K + 192 B V per pos per vanilla layer) + per-pos fp32
  scale-corrections if needed; KDA state 3×64×64 fp32 per layer (48 KB × 9).
- Everything-else ops (norms, quant, rope, softmax, sigmoid/softplus/silu/tanh)
  must be vectorized too (vector exp via polynomial (see notes below), fp32).
  Watch out: these must stay numerically close to libm/torch (≤ ~2 ulp), NOT
  fast-math sloppy. Where exactness vs torch matters most (final softmax/tanh,
  silu, softplus, sigmoid), prefer high-accuracy vector implementations and
  VERIFY component divergence in test_components.
- Approximations that change math (attention low-prob skip, prior sparsity
  short-circuit — note prior sparse kernel is EXACT: skipping q=0 terms changes
  nothing) must default to settings that keep the e2e loss criterion green and
  be individually toggleable for measurement.

## 9. Benchmark & report requirements (final deliverable)

1. Throughput (tokens/s) over the full 1024-article test set (measure ≥ 3 runs,
   report median; state measured CPU clock). Report with profiling instrumentation
   disabled, and the instrumented number separately.
2. Theoretical max throughput = Σ over components min(compute bound, bandwidth
   bound), counting BOTH multiplies and adds as ops (a MAC = 2 ops) against
   measured peak op rates and measured bandwidths at the cache level each
   component actually streams from. Report the whole-transformer theoretical
   max for BOTH packed-int4 and unpacked-int8 weight storage, state which one
   the implementation uses, and per-part maxima with/without packing where the
   tradeoff exists.
3. Per-part table measured INSIDE full-transformer inference (rdtsc sections,
   toggleable): parts = {int4×int8 matmuls (all), vanilla attention mechanism,
   kimi linear attention mechanism (incl. conv, gates nonlinearity, gated norm,
   beta), everything else (norms, residual/skip/token connections, embedding,
   prior embedding sparse matmul? NO — prior embedding is an int4×int8 matmul →
   count it in matmuls; rope, quantize steps, softcap+softmax head, KV ring
   bookkeeping)}: fraction of runtime + achieved throughput as fraction of that
   part's theoretical max (skip theoretical max for "everything else").
4. L3 usage: analytic hot-footprint + empirical co-residency curve (SMT sibling
   or same-CCX core running a configurable-footprint L3 thrasher; find the
   thrasher footprint at which transformer throughput drops by >5%) →
   "another program could use ~X MB of the 16 MB CCX L3 without slowing us much".
5. Loss check summary from test_e2e (absolute numbers + relative delta).

## 10. Repository layout for this effort

```
cpp_infer/
  SPEC.md               (this file)
  KIMI_SEMANTICS.md     (exact KDA/conv/gated-norm math, validated)
  MACHINE.md            (measured peaks: clock, ALU, BW per level, div/exp)
  data/                 (weights.bin, test files, dumps/)   [gitignored, large]
  src/                  (C++ sources)
  bench/                (microbenchmarks, thrasher)
  Makefile
pysrc/export_weights.py
pysrc/export_testdata.py
```
Run Python via `.venv/bin/python` from repo root (`/root/fx2-cmix-transformer`).
GPU (RTX 4070) is available for reference runs.
