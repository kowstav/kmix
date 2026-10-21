#include "arena_build.h"

#include <sys/mman.h>

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "../attn_window.h"
#include "../weights_io.h"
#include "glue.h"
#include "qmat_cpu.h"

namespace fx2 {
namespace opt {

namespace {

[[noreturn]] void die(const char* msg) {
  std::fprintf(stderr, "arena_build: %s\n", msg);
  std::exit(1);
}

constexpr size_t round64(size_t x) { return (x + 63) & ~size_t(63); }

}  // namespace

void HugeBuf::alloc(size_t n) {
  bytes = (n + (size_t(2) << 20) - 1) & ~((size_t(2) << 20) - 1);
  void* m = ::mmap(nullptr, bytes, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  if (m == MAP_FAILED) die("mmap failed");
  ::madvise(m, bytes, MADV_HUGEPAGE);
  std::memset(m, 0, bytes);  // touch every page
  p = static_cast<uint8_t*>(m);
}

HugeBuf::~HugeBuf() {
  if (p) ::munmap(p, bytes);
}

void OptModel::load(const char* weights_path) {
  // accept both the raw FX2TFW01 file and the losslessly compressed
  // FX2TFWC1/FX2TFWC2 files (bit-identical tensors either way)
  char magic[8] = {0};
  if (FILE* f = std::fopen(weights_path, "rb")) {
    if (std::fread(magic, 1, 8, f) != 8) magic[0] = 0;
    std::fclose(f);
  }
  WeightsFile wf = std::memcmp(magic, "FX2TFWC", 7) == 0
                       ? WeightsFile::load_compressed(weights_path)
                       : WeightsFile::load(weights_path);

  {  // config sanity (same checks as the naive loader)
    const WTensor& ci = wf.get("config.ints", DT_I32, {11});
    // want[6] = the sliding attention window this binary was compiled for
    // (-DATTN_WIN, default 1024): the weights must carry the same window
    const int32_t want[11] = {V, D, NL, DH, NH, DMLP, ATTN_WIN, DH, NH, 4, 10000};
    for (int i = 0; i < 11; i++)
      if (ci.i32()[i] != want[i]) {
        char msg[160];
        std::snprintf(msg, sizeof(msg),
                      "config.ints mismatch at index %d: weights file has %d, "
                      "binary expects %d%s",
                      i, static_cast<int>(ci.i32()[i]), static_cast<int>(want[i]),
                      i == 6 ? " (attention window ATTN_WIN)" : "");
        die(msg);
      }
    const WTensor& ck = wf.get("config.kimi", DT_I32, {NL});
    for (int i = 0; i < NL; i++)
      if ((ck.i32()[i] != 0) != KIMI_L(i)) die("config.kimi mismatch");
    // per-layer window multipliers (attn_window.h ATTN_WIN_MULTS; SPEC.md section 3.5): config.window_mults int32[NV], one
    // per vanilla layer in layer order (12 layers: 3, 7, 11); absent = every layer at the base window ATTN_WIN
    {
      const int32_t* wm = wf.has("config.window_mults") ? wf.get("config.window_mults", DT_I32, {static_cast<uint32_t>(attn_win::NV)}).i32() : nullptr;
      for (int vi = 0; vi < attn_win::NV; vi++) {
        const int file_m = wm ? static_cast<int>(wm[vi]) : 1;
        if (file_m != attn_win::mult(vi)) {
          char msg[200];
          std::snprintf(msg, sizeof(msg),
                        "config.window_mults mismatch at vanilla layer %d: weights file has x%d, binary built for x%d "
                        "(rebuild with -DATTN_WIN_MULTS=<the file's multipliers>)", vi, file_m, attn_win::mult(vi));
          die(msg);
        }
      }
    }
    // activation quantization mode (SPEC.md section 2a, tf_arch.h TF_ACTQ_DYN): config.actq_dynamic_mm = 1 marks a
    // checkpoint with dynamic per-token activation scales (no .quantize_activation.scale tensors in the file)
    const int file_dyn = wf.has("config.actq_dynamic_mm") ? wf.get("config.actq_dynamic_mm", DT_I32, {1}).i32()[0] : 0;
    if ((file_dyn != 0) != (TF_ACTQ_DYN != 0))
      die(TF_ACTQ_DYN ? "config.actq_dynamic_mm mismatch: weights have static activation scales, binary built with TF_ACTQ_DYN=1"
                      : "config.actq_dynamic_mm mismatch: weights use dynamic per-token activation scales (rebuild with -DTF_ACTQ_DYN=1)");
  }

#if QMAT_CODEBOOK
  // codebook weights (qmat.h): <prefix>.weight.q holds level indices in [-7,7]; <prefix>.weight.codebook the 15
  // signed level values (|v| <= QMAT_WMAX) in units of grid * row scale (config.codebook_grid).
  const float cb_grid = wf.get("config.codebook_grid", DT_F32, {1}).f32()[0];
  if (!(cb_grid > 0.0f)) die("codebook grid not positive");
  if (wf.get("config.codebook_max_int", DT_I32, {1}).i32()[0] > QMAT_WMAX) die("codebook max int exceeds QMAT_WMAX (rebuild with a larger -DQMAT_WMAX)");
  auto load_codebook = [&](const std::string& prefix, int8_t cb[16]) {
    const WTensor& t = wf.get(prefix + ".weight.codebook", DT_I8, {15});
    for (int k = 0; k < 15; k++) {
      cb[k] = t.i8()[k];
      if (cb[k] < -QMAT_WMAX || cb[k] > QMAT_WMAX) die("codebook value out of range");
    }
    cb[15] = 0;
  };
  // index -> value for a whole matrix (row-major int8 of the same shape)
  std::vector<int8_t> mapped;
  auto map_indices = [&](const WTensor& wq, const int8_t cb[16]) -> const int8_t* {
    mapped.resize(wq.numel);
    for (size_t i = 0; i < wq.numel; i++) {
      const int q = wq.i8()[i];
      if (q < -7 || q > 7) die("level index out of [-7,7]");
      mapped[i] = cb[q + 7];
    }
    return mapped.data();
  };
#endif

  // AVX-512 fast path (qmat.h TF_AVX512): decided once per process from cpuid; the dense 192-in sites are then
  // built as QPackedCB arenas (half the stream bytes) and model_opt.cpp calls the qmat_avx512.h kernels.
  avx512 = cpu_has_avx512_vnni();
  if (const char* v = std::getenv("FX2_VERBOSE_ISA"))
    if (v[0] == '1') std::fprintf(stderr, "transformer kernels: %s\n", avx512 ? "AVX-512 VNNI (packed int4 + LUT arenas)" : "AVX2 (unpacked int8 arenas)");

  pool.alloc(size_t(16) << 20);
  size_t off = 0;
  auto take = [&](size_t n) -> uint8_t* {
    off = round64(off);
    uint8_t* q = pool.p + off;
    off += n;
    if (off + QMAT_TAIL_SLACK > pool.bytes) die("weight pool overflow");
    return q;
  };

  // the static activation scale of a matmul site (fp32 of the bf16 bits, > 0). Under TF_ACTQ_DYN the file carries
  // none (pysrc/export_weights.py skips the zero buffers) and the arenas fold only the weight row scales: 1.0.
  auto act_scale = [&](const std::string& prefix) -> float {
#if TF_ACTQ_DYN
    if (wf.has(prefix + ".quantize_activation.scale")) die("dynamic build, but the weights file has a static activation scale");
    return 1.0f;
#else
    const WTensor& sa = wf.get(prefix + ".quantize_activation.scale", DT_BF16, {1});
    const float s_act = bf16_to_f32(sa.bf16_bits()[0]);
    if (!(s_act > 0.0f)) die("activation scale not positive");
    return s_act;
#endif
  };

  // dense arena site in stream order
  auto qsite = [&](const std::string& prefix, int d_out, int d_in,
                   bool biased) -> QSite {
    const WTensor& wq =
        wf.get(prefix + ".weight.q", DT_I8,
               {static_cast<uint32_t>(d_out), static_cast<uint32_t>(d_in)});
    const WTensor& ws = wf.get(prefix + ".weight.scale", DT_BF16,
                               {static_cast<uint32_t>(d_out)});
    QSite s;
    s.s_act = act_scale(prefix);   // 1.0 under TF_ACTQ_DYN: fold = row scale only, the token scale is applied per token
    std::vector<float> fold(d_out);
    for (int o = 0; o < d_out; o++)
      fold[o] = s.s_act * bf16_to_f32(ws.bf16_bits()[o]);
#if QMAT_CODEBOOK
    int8_t cb[16];
    load_codebook(prefix, cb);
    for (int o = 0; o < d_out; o++) fold[o] *= cb_grid;
    [[maybe_unused]] const int8_t* cbp = cb;   // QPackedCB LUT (TF_AVX512)
#else
    [[maybe_unused]] const int8_t* cbp = nullptr;   // identity LUT: nibble = value + 7
#endif
#if TF_AVX512
    // AVX-512 host: packed int4 + LUT arena for the 192-in sites (same corr/fold conventions, bit-identical
    // outputs); the 64-in gate-down matrices stay unpacked (their npair-1 packed kernel is slower)
    if (avx512 && d_in != 64) {
      uint8_t* dst = take(qpackedcb_bytes(d_out, d_in));
      s.pm = qpackedcb_build(dst, wq.i8(), cbp, fold.data(), d_out, d_in, biased);
      return s;
    }
#endif
    uint8_t* dst = take(qdense_bytes(d_out, d_in));
#if QMAT_CODEBOOK
    s.m = qdense_build(dst, map_indices(wq, cb), fold.data(), d_out, d_in, biased);
#else
    s.m = qdense_build(dst, wq.i8(), fold.data(), d_out, d_in, biased);
#endif
    return s;
  };

  // int4 sparse-column arena site (d_out must be 192): [fold | cols]
  auto qsp4 = [&](const std::string& prefix, int d_in,
                  float* s_act_out) -> QSparse4 {
    const WTensor& wq =
        wf.get(prefix + ".weight.q", DT_I8,
               {static_cast<uint32_t>(D), static_cast<uint32_t>(d_in)});
    const WTensor& ws = wf.get(prefix + ".weight.scale", DT_BF16,
                               {static_cast<uint32_t>(D)});
    const float s_act = act_scale(prefix);
    *s_act_out = s_act;
    std::vector<float> fold(D);
    for (int o = 0; o < D; o++)
      fold[o] = s_act * bf16_to_f32(ws.bf16_bits()[o]);
    float* foldp = reinterpret_cast<float*>(take(sizeof(float) * D));
    uint8_t* cols = take(qsparse4_bytes(d_in));
#if QMAT_CODEBOOK
    // nibbles stay level indices (q + 7); the kernel maps them through m.lut
    int8_t cb[16];
    load_codebook(prefix, cb);
    for (int o = 0; o < D; o++) fold[o] *= cb_grid;
    QSparse4 m4 = qsparse4_build(cols, foldp, wq.i8(), fold.data(), D, d_in);
    for (int k = 0; k < 16; k++) m4.lut[k] = m4.lut[16 + k] = cb[k];
    return m4;
#else
    return qsparse4_build(cols, foldp, wq.i8(), fold.data(), D, d_in);
#endif
  };

  auto f32block = [&](const float* src, size_t n) -> float* {
    float* p = reinterpret_cast<float*>(take(sizeof(float) * n));
    std::memcpy(p, src, sizeof(float) * n);
    return p;
  };

#if QMAT_SMALL_W8
  // 8-bit small matmuls (qmat.h): plain int8 values in [-127,127], no codebook, exact int16-widened kernel
  auto qw8site = [&](const std::string& prefix, int d_out, int d_in, bool biased, float* s_act_out) -> QW8 {
    const WTensor& wq = wf.get(prefix + ".weight.q", DT_I8, {static_cast<uint32_t>(d_out), static_cast<uint32_t>(d_in)});
    const WTensor& ws = wf.get(prefix + ".weight.scale", DT_BF16, {static_cast<uint32_t>(d_out)});
    const float s_act = act_scale(prefix);
    if (s_act_out) *s_act_out = s_act;
    std::vector<float> fold(d_out);
    for (int o = 0; o < d_out; o++) fold[o] = s_act * bf16_to_f32(ws.bf16_bits()[o]);
    const int rows_padded = qmat_round_up(d_out, 8);
    int8_t* w = reinterpret_cast<int8_t*>(take(qw8_bytes(d_out, d_in)));
    int32_t* corr = reinterpret_cast<int32_t*>(take(sizeof(int32_t) * rows_padded));
    float* fld = reinterpret_cast<float*>(take(sizeof(float) * rows_padded));
    return qw8_build(w, corr, fld, wq.i8(), fold.data(), d_out, d_in, biased);
  };
#endif

  // ---- stream, in per-token consumption order ----
#if QMAT_SMALL_W8
  prior8 = qw8site("prior_embedding", D, V, false, &prior_s_act);
#else
  prior = qsp4("prior_embedding", V, &prior_s_act);
#endif

  {
    const WTensor& sw = wf.get("skip_connection_weights.value", DT_F32, {static_cast<uint32_t>(NSKIP)});
    for (int i = 0; i < NSKIP; i++) skip_w[i] = sw.f32()[i];
  }

  int ki = 0, vi = 0;
  for (int l = 0; l < NL; l++) {
    std::string b = "blocks." + std::to_string(l) + ".";
    rsc[l] =
        wf.get(b + "residual_stream_coefficient.value", DT_F32, {1}).f32()[0];
    tec[l] =
        wf.get(b + "token_embedding_coefficient.value", DT_F32, {1}).f32()[0];
    std::string a = b + "attention.";

    if (KIMI_L(l)) {
      KimiArenas& L = kimi[ki];
      layer2kimi[l] = ki;
      L.qp = qsite(a + "query_projection", D, D, true);
      L.kp = qsite(a + "key_projection", D, D, true);
      L.vp = qsite(a + "value_projection", D, D, true);
      L.fg_up = qsite(a + "forget_gate_projection.up", DH, D, true);
      L.fg_down = qsite(a + "forget_gate_projection.down", D, DH, true);
      L.og_up = qsite(a + "output_gate_projection.up", DH, D, true);
      L.og_down = qsite(a + "output_gate_projection.down", D, DH, true);

      {
        const WTensor& bw =
            wf.get(a + "beta_projection.weight", DT_F32, {NH, D});
        L.beta_w = f32block(bw.f32(), size_t(NH) * D);
      }
      const char* convs[3] = {"query_convolution.weight",
                              "key_convolution.weight",
                              "value_convolution.weight"};
      for (int c = 0; c < 3; c++) {
        const WTensor& cw = wf.get(a + convs[c], DT_F32, {D, 4});
        float* wt = reinterpret_cast<float*>(take(sizeof(float) * 4 * D));
        for (int j = 0; j < 4; j++)  // tap-major repack, same as naive
          for (int ch = 0; ch < D; ch++) wt[j * D + ch] = cw.f32()[ch * 4 + j];
        L.kw.conv_w[c] = wt;
      }
      {
        const WTensor& dt = wf.get(a + "dt_bias", DT_F32, {D});
        L.kw.dt_bias = f32block(dt.f32(), D);
      }
      {
        const WTensor& gw =
            wf.get(a + "output_fused_norm_gate.weight", DT_F32, {DH});
        L.kw.gn_w = f32block(gw.f32(), DH);
      }
      {
        const WTensor& al = wf.get(a + "log_baseline_decay_rate", DT_F32, {NH});
        for (int h = 0; h < NH; h++) L.kw.a_neg[h] = -std::exp(al.f32()[h]);
      }
      L.op = qsite(a + "output_projection", D, D, true);
      ki++;
    } else {
      VanArenas& L = van[vi];
      layer2van[l] = vi;
      L.qp = qsite(a + "query_projection", D, D, true);
      L.kp = qsite(a + "key_projection", D, D, true);
      L.vp = qsite(a + "value_projection", D, D, true);
      L.op = qsite(a + "output_projection", D, D, true);
      const WTensor& qs = wf.get(a + "quantize_queries.scale", DT_BF16, {NH});
      const WTensor& ks = wf.get(a + "quantize_keys.scale", DT_BF16, {NH});
      const WTensor& vs = wf.get(a + "quantize_values.scale", DT_BF16, {NH});
      for (int h = 0; h < NH; h++) {
        L.sq[h] = bf16_to_f32(qs.bf16_bits()[h]);
        L.sk[h] = bf16_to_f32(ks.bf16_bits()[h]);
        L.sv[h] = bf16_to_f32(vs.bf16_bits()[h]);
        L.coef[h] = 0.125f * L.sq[h] * L.sk[h];
      }
      vi++;
    }

    mlp[l].up = qsite(b + "mlp.up", DMLP, D, true);
    mlp[l].down = qsp4(b + "mlp.down", DMLP, &mlp[l].down_s_act);
  }
  if (vi != (NL + 3) / 4 || ki != NL - (NL + 3) / 4) die("layer pattern mismatch");  // vanilla attention every 4th layer from the end (3 of 12, 2 of 8)

#if QMAT_SMALL_W8
  {
    unembed.s_act = act_scale("unembedding");   // rms_norm_quant192 reads unembed.s_act (static builds)
    unembed8 = qw8site("unembedding", V, D, true, nullptr);
  }
#else
  unembed = qsite("unembedding", V, D, true);
#endif
  stream_bytes = round64(off);

  // ---- non-stream data: tail slack gap, then the normed embedding table ----
  off += QMAT_TAIL_SLACK;
  {
    const WTensor& eq = wf.get("embedding.weight.q", DT_I8, {V, D});
    const WTensor& es = wf.get("embedding.weight.scale", DT_BF16, {V});
    std::vector<float> rs(V);
    for (int c = 0; c < V; c++) rs[c] = bf16_to_f32(es.bf16_bits()[c]);
    float* table = reinterpret_cast<float*>(take(sizeof(float) * V * D));
#if QMAT_CODEBOOK && !QMAT_SMALL_W8
    int8_t cb[16];
    load_codebook("embedding", cb);
    for (int c = 0; c < V; c++) rs[c] *= cb_grid;
    build_normed_embedding_table(map_indices(eq, cb), rs.data(), table);
#else
    build_normed_embedding_table(eq.i8(), rs.data(), table);   // plain int values (int4, or int8 with QMAT_SMALL_W8)
#endif
    tok_table = table;
  }

  {
    const WTensor& fi = wf.get("rope.inv_freq", DT_F32, {32});
    std::memcpy(inv_freq, fi.f32(), sizeof(inv_freq));
    const WTensor& si = wf.get("rope.sin", DT_F32,
                               {static_cast<uint32_t>(ROPE_LEN), 32});
    const WTensor& co = wf.get("rope.cos", DT_F32,
                               {static_cast<uint32_t>(ROPE_LEN), 32});
    rope_sin.assign(si.f32(), si.f32() + size_t(ROPE_LEN) * 32);
    rope_cos.assign(co.f32(), co.f32() + size_t(ROPE_LEN) * 32);
  }
}

}  // namespace opt
}  // namespace fx2
