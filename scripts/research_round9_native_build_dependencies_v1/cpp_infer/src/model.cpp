#include "model.h"
#include "opt/qmat.h"
#include "opt/tf_arch.h"

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "kernels.h"
#include "weights_io.h"

namespace fx2 {

namespace {

constexpr int V = 205, D = 192, NL = opt::arch::NL, DH = 64, NH = 3, DMLP = opt::arch::DMLP, NSKIP = opt::arch::NSKIP;  // opt/tf_arch.h
constexpr int WIN = ATTN_WIN;  // base attention window (attn_window.h -DATTN_WIN, default 1024; config.ints[6])
constexpr int WMAX = attn_win::WMAX;  // largest per-layer window (ATTN_WIN x the largest -DATTN_WIN_MULTS entry)
constexpr int ROPE_LEN = 131072;
constexpr int PRIOR_STRIDE = 208;  // 205 padded to a multiple of 16
constexpr bool KIMI(int l) { return opt::arch::KIMI.v[l]; }

[[noreturn]] void die(const char* msg) {
  std::fprintf(stderr, "model: %s\n", msg);
  std::exit(1);
}

// 64B-aligned bump arena for repacked weights
struct Arena {
  uint8_t* base = nullptr;
  size_t cap = 0, used = 0;

  void init(size_t bytes) {
    bytes = (bytes + 63) & ~size_t(63);
    base = static_cast<uint8_t*>(std::aligned_alloc(64, bytes));
    if (!base) die("out of memory");
    cap = bytes;
    used = 0;
  }
  void* take(size_t bytes) {
    used = (used + 63) & ~size_t(63);
    if (used + bytes > cap) die("arena overflow");
    void* p = base + used;
    used += bytes;
    return p;
  }
  ~Arena() { std::free(base); }
};

}  // namespace

// quantized linear: int8 rows (padded stride) + folded per-row fp32 scales
struct QLinear {
  const int8_t* w = nullptr;
  const float* fold = nullptr;  // s_act * s_w[o]
  float s_act = 0.0f;
  int d_out = 0, d_in = 0, stride = 0;
};

struct KimiLayer {
  QLinear qp, kp, vp, fg_up, fg_down, og_up, og_down, op;
  const float* wt_q = nullptr;  // conv weights, tap-major [4][192]
  const float* wt_k = nullptr;
  const float* wt_v = nullptr;
  const float* beta_w = nullptr;   // [3][192]
  const float* dt_bias = nullptr;  // [192]
  const float* gn_w = nullptr;     // [64]
  float a_neg[NH] = {};            // -exp(A_log[h])
};

struct VanLayer {
  QLinear qp, kp, vp, op;
  float sq[NH] = {}, sk[NH] = {}, sv[NH] = {};
  float coef[NH] = {};  // 0.125 * sq[h] * sk[h]
};

struct MlpW {
  QLinear up, down;
};

struct KimiState {
  alignas(64) float S[NH][DH * DH];  // [head][k*64 + v]
  alignas(64) float hist[3][3][D];   // [conv q/k/v][tap: 0=t-3,1=t-2,2=t-1][ch]
};

struct VanState {
  alignas(64) int8_t kring[WMAX][D];  // rows [0, attn_win::win(vi)) used by vanilla layer vi
  alignas(64) int8_t vring[WMAX][D];
};

struct TransformerImpl {
  Arena wa, fa;

  QLinear prior_lin, unembed;
  KimiLayer kimi[opt::arch::NK];
  VanLayer van[opt::arch::NV];
  MlpW mlp[NL];
  int layer2kimi[NL] = {};
  int layer2van[NL] = {};
  float rsc[NL] = {}, tec[NL] = {};
  float skip_w[NSKIP] = {};
  const float* tok_table = nullptr;  // 205 x 192 normed embedding rows
  const float* rope_sin = nullptr;   // 131072 x 32
  const float* rope_cos = nullptr;
  float inv_freq[32] = {};

  // streaming state
  KimiState kst[opt::arch::NK];
  VanState vst[opt::arch::NV];
  float skip_store[NSKIP][D] = {};
  int64_t t = 0;
  int64_t rope_off = 0;
  bool lowprob_skip = false;
  float lowprob_threshold = 21.0f;

  alignas(64) float logits[V] = {};
  Transformer::CaptureFn cap_fn;
  Transformer::BlockInputOverrideFn override_fn;

  // scratch
  alignas(64) int8_t q8[DMLP] = {};
  alignas(64) float xb[D] = {}, xnb[D] = {}, yb[D] = {}, h768[DMLP] = {};
  alignas(64) float prior_f32[PRIOR_STRIDE] = {};

  void load(const char* path);
  QLinear load_qlinear(const WeightsFile& wf, const std::string& prefix,
                       int d_out, int d_in);
  void begin(int64_t rope_position_offset);
  void step(uint8_t token, const float* prior, float* probs_out);
  void kimi_attention(int ki, int l, const float* xn, float* y);
  void van_attention(int vi, int l, const float* xn, float* y);

  void cap(const char* name, const float* d, int n) {
    if (cap_fn) cap_fn(name, d, n);
  }
  void capL(int l, const char* comp, const float* d, int n) {
    if (!cap_fn) return;
    char nm[64];
    std::snprintf(nm, sizeof nm, "%02d_%s", l, comp);
    cap_fn(nm, d, n);
  }

  // quantized linear out = L(in), in[0..n) (n = L.d_in; the int8 vector is zero-padded to L.stride):
  // activation quantized with the learned static scale L.s_act, or (TF_ACTQ_DYN, tf_arch.h) with the token's
  // dynamic scale s = max(max|in|, 1e-12)/127 -- then y = (fold * float(dot)) * s as two separately rounded fp32
  // multiplies (kernels.cpp scale_vec), exactly the opt kernels' (e)-(h) epilogues (src/opt/qmat_dense.h).
  void qlin(const QLinear& L, const float* in, int n, float* out) {
#if TF_ACTQ_DYN
    const float s = dyn_act_scale(in, n);
    quantize_i8(in, n, L.stride, s, q8);
    qmatvec(L.w, L.stride, L.fold, L.d_out, q8, out);
    scale_vec(out, L.d_out, s);
#else
    quantize_i8(in, n, L.stride, L.s_act, q8);
    qmatvec(L.w, L.stride, L.fold, L.d_out, q8, out);
#endif
  }
};

#if QMAT_CODEBOOK
namespace {
// codebook weights (opt/qmat.h): level index -> signed value, units of grid * row scale
void load_codebook(const WeightsFile& wf, const std::string& prefix, int8_t cb[16]) {
  const WTensor& t = wf.get(prefix + ".weight.codebook", DT_I8, {15});
  for (int k = 0; k < 15; k++) {
    cb[k] = t.i8()[k];
    if (cb[k] < -QMAT_WMAX || cb[k] > QMAT_WMAX) die("codebook value out of range");
  }
  cb[15] = 0;
}
float codebook_grid(const WeightsFile& wf) {
  const float g = wf.get("config.codebook_grid", DT_F32, {1}).f32()[0];
  if (!(g > 0.0f)) die("codebook grid not positive");
  return g;
}
}  // namespace
#endif

QLinear TransformerImpl::load_qlinear(const WeightsFile& wf,
                                      const std::string& prefix, int d_out,
                                      int d_in) {
  const WTensor& wq =
      wf.get(prefix + ".weight.q", DT_I8,
             {static_cast<uint32_t>(d_out), static_cast<uint32_t>(d_in)});
  const WTensor& ws = wf.get(prefix + ".weight.scale", DT_BF16,
                             {static_cast<uint32_t>(d_out)});

  QLinear ql;
  ql.d_out = d_out;
  ql.d_in = d_in;
  ql.stride = (d_in + 15) & ~15;
  int8_t* w = static_cast<int8_t*>(wa.take(size_t(d_out) * ql.stride));
  const int8_t* src = wq.i8();
  // QMAT_SMALL_W8: the prior projection and the unembedding carry plain int8 values in [-127,127] (no codebook)
  const bool small8 = QMAT_SMALL_W8 && (prefix == "prior_embedding" || prefix == "unembedding");
  if (!small8)
    for (size_t i = 0; i < wq.numel; i++)
      if (src[i] < -7 || src[i] > 7) die("weight int out of [-7,7]");
  float grid = 1.0f;
#if QMAT_CODEBOOK
  std::vector<int8_t> mapped(wq.numel);
  if (!small8) {
    int8_t cb[16];
    load_codebook(wf, prefix, cb);
    grid = codebook_grid(wf);
    for (size_t i = 0; i < wq.numel; i++) mapped[i] = cb[src[i] + 7];
    src = mapped.data();
  }
#endif
  for (int o = 0; o < d_out; o++) {
    std::memcpy(w + size_t(o) * ql.stride, src + size_t(o) * d_in, d_in);
    std::memset(w + size_t(o) * ql.stride + d_in, 0,
                size_t(ql.stride - d_in));
  }

  float* fold = static_cast<float*>(fa.take(sizeof(float) * d_out));
#if TF_ACTQ_DYN
  // dynamic per-token activation scales: the file carries no .quantize_activation.scale; fold = row scale only
  if (wf.has(prefix + ".quantize_activation.scale")) die("dynamic build, but the weights file has a static activation scale");
  ql.s_act = 1.0f;
#else
  const WTensor& sa =
      wf.get(prefix + ".quantize_activation.scale", DT_BF16, {1});
  ql.s_act = bf16_to_f32(sa.bf16_bits()[0]);
  if (!(ql.s_act > 0.0f)) die("activation scale not positive");
#endif
  for (int o = 0; o < d_out; o++)
    fold[o] = ql.s_act * bf16_to_f32(ws.bf16_bits()[o]) * grid;
  ql.w = w;
  ql.fold = fold;
  return ql;
}

void TransformerImpl::load(const char* path) {
  WeightsFile wf = WeightsFile::load(path);

  // config sanity
  {
    const WTensor& ci = wf.get("config.ints", DT_I32, {11});
    const int32_t want[11] = {V, D, NL, DH, NH, DMLP, WIN, DH, NH, 4, 10000};
    for (int i = 0; i < 11; i++)
      if (ci.i32()[i] != want[i]) die("config.ints mismatch");
    const WTensor& ck = wf.get("config.kimi", DT_I32, {NL});
    for (int i = 0; i < NL; i++)
      if ((ck.i32()[i] != 0) != KIMI(i)) die("config.kimi mismatch");
    // per-layer window multipliers (attn_window.h ATTN_WIN_MULTS; SPEC.md section 3.5): config.window_mults int32[NV], one
    // per vanilla layer in layer order; absent = every layer at the base window
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
    // activation quantization mode (SPEC.md section 2a): config.actq_dynamic_mm = 1 <-> a -DTF_ACTQ_DYN=1 build
    const int file_dyn = wf.has("config.actq_dynamic_mm") ? wf.get("config.actq_dynamic_mm", DT_I32, {1}).i32()[0] : 0;
    if ((file_dyn != 0) != (TF_ACTQ_DYN != 0))
      die(TF_ACTQ_DYN ? "config.actq_dynamic_mm mismatch: weights have static activation scales, binary built with TF_ACTQ_DYN=1"
                      : "config.actq_dynamic_mm mismatch: weights use dynamic per-token activation scales (rebuild with -DTF_ACTQ_DYN=1)");
  }

  wa.init(size_t(8) << 20);
  fa.init(size_t(40) << 20);

  // normed token embedding table
  {
    const WTensor& eq = wf.get("embedding.weight.q", DT_I8, {V, D});
    const WTensor& es = wf.get("embedding.weight.scale", DT_BF16, {V});
    float* table = static_cast<float*>(fa.take(sizeof(float) * V * D));
#if QMAT_CODEBOOK && !QMAT_SMALL_W8
    int8_t ecb[16];
    load_codebook(wf, "embedding", ecb);
    const float egrid = codebook_grid(wf);
#endif
    for (int c = 0; c < V; c++) {
      float s = bf16_to_f32(es.bf16_bits()[c]);
      float* row = table + size_t(c) * D;
      for (int i = 0; i < D; i++) {
#if QMAT_CODEBOOK && !QMAT_SMALL_W8
        row[i] = static_cast<float>(ecb[eq.i8()[c * D + i] + 7]) * (s * egrid);
#else
        row[i] = static_cast<float>(eq.i8()[c * D + i]) * s;   // int4, or int8 with QMAT_SMALL_W8
#endif
      }
      rms_norm_vec(row, row, D);
    }
    tok_table = table;
  }

  prior_lin = load_qlinear(wf, "prior_embedding", D, V);
  unembed = load_qlinear(wf, "unembedding", V, D);

  {
    const WTensor& sw = wf.get("skip_connection_weights.value", DT_F32, {static_cast<uint32_t>(NSKIP)});
    for (int i = 0; i < NSKIP; i++) skip_w[i] = sw.f32()[i];
  }

  int ki = 0, vi = 0;
  for (int l = 0; l < NL; l++) {
    std::string b = "blocks." + std::to_string(l) + ".";
    rsc[l] = wf.get(b + "residual_stream_coefficient.value", DT_F32, {1}).f32()[0];
    tec[l] = wf.get(b + "token_embedding_coefficient.value", DT_F32, {1}).f32()[0];
    std::string a = b + "attention.";

    if (KIMI(l)) {
      KimiLayer& L = kimi[ki];
      layer2kimi[l] = ki;
      L.qp = load_qlinear(wf, a + "query_projection", D, D);
      L.kp = load_qlinear(wf, a + "key_projection", D, D);
      L.vp = load_qlinear(wf, a + "value_projection", D, D);
      L.fg_up = load_qlinear(wf, a + "forget_gate_projection.up", DH, D);
      L.fg_down = load_qlinear(wf, a + "forget_gate_projection.down", D, DH);
      L.og_up = load_qlinear(wf, a + "output_gate_projection.up", DH, D);
      L.og_down = load_qlinear(wf, a + "output_gate_projection.down", D, DH);
      L.op = load_qlinear(wf, a + "output_projection", D, D);

      const char* convs[3] = {"query_convolution.weight",
                              "key_convolution.weight",
                              "value_convolution.weight"};
      const float* dst[3];
      for (int c = 0; c < 3; c++) {
        const WTensor& cw = wf.get(a + convs[c], DT_F32, {D, 4});
        float* wt = static_cast<float*>(fa.take(sizeof(float) * 4 * D));
        for (int j = 0; j < 4; j++)
          for (int ch = 0; ch < D; ch++) wt[j * D + ch] = cw.f32()[ch * 4 + j];
        dst[c] = wt;
      }
      L.wt_q = dst[0];
      L.wt_k = dst[1];
      L.wt_v = dst[2];

      {
        const WTensor& bw = wf.get(a + "beta_projection.weight", DT_F32, {NH, D});
        float* p = static_cast<float*>(fa.take(sizeof(float) * NH * D));
        std::memcpy(p, bw.f32(), sizeof(float) * NH * D);
        L.beta_w = p;
      }
      {
        const WTensor& dt = wf.get(a + "dt_bias", DT_F32, {D});
        float* p = static_cast<float*>(fa.take(sizeof(float) * D));
        std::memcpy(p, dt.f32(), sizeof(float) * D);
        L.dt_bias = p;
      }
      {
        const WTensor& gw =
            wf.get(a + "output_fused_norm_gate.weight", DT_F32, {DH});
        float* p = static_cast<float*>(fa.take(sizeof(float) * DH));
        std::memcpy(p, gw.f32(), sizeof(float) * DH);
        L.gn_w = p;
      }
      {
        const WTensor& al = wf.get(a + "log_baseline_decay_rate", DT_F32, {NH});
        for (int h = 0; h < NH; h++) L.a_neg[h] = -std::exp(al.f32()[h]);
      }
      ki++;
    } else {
      VanLayer& L = van[vi];
      layer2van[l] = vi;
      L.qp = load_qlinear(wf, a + "query_projection", D, D);
      L.kp = load_qlinear(wf, a + "key_projection", D, D);
      L.vp = load_qlinear(wf, a + "value_projection", D, D);
      L.op = load_qlinear(wf, a + "output_projection", D, D);
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

    mlp[l].up = load_qlinear(wf, b + "mlp.up", DMLP, D);
    mlp[l].down = load_qlinear(wf, b + "mlp.down", D, DMLP);
  }
  if (vi != (NL + 3) / 4 || ki != NL - (NL + 3) / 4) die("layer pattern mismatch");  // vanilla attention every 4th layer from the end (3 of 12, 2 of 8)

  {
    const WTensor& fi = wf.get("rope.inv_freq", DT_F32, {32});
    std::memcpy(inv_freq, fi.f32(), sizeof(inv_freq));
    const WTensor& si = wf.get("rope.sin", DT_F32, {ROPE_LEN, 32});
    const WTensor& co = wf.get("rope.cos", DT_F32, {ROPE_LEN, 32});
    float* s = static_cast<float*>(fa.take(sizeof(float) * ROPE_LEN * 32));
    float* c = static_cast<float*>(fa.take(sizeof(float) * ROPE_LEN * 32));
    std::memcpy(s, si.f32(), sizeof(float) * ROPE_LEN * 32);
    std::memcpy(c, co.f32(), sizeof(float) * ROPE_LEN * 32);
    rope_sin = s;
    rope_cos = c;
  }

  std::memset(kst, 0, sizeof(kst));
  std::memset(vst, 0, sizeof(vst));
}

void TransformerImpl::begin(int64_t rope_position_offset) {
  std::memset(kst, 0, sizeof(kst));  // KDA states and conv histories to zero
  t = 0;                             // invalidates the KV rings
  rope_off = rope_position_offset;
}

void TransformerImpl::kimi_attention(int ki, int l, const float* xn, float* y) {
  KimiLayer& L = kimi[ki];
  KimiState& st = kst[ki];
  alignas(32) float bq[D], bk[D], bv[D], cq[D], ck[D], cv[D];
  alignas(32) float fu[DH], graw[D], og192[D], braw[NH];
  alignas(32) float o192[D], gn[D];

  qlin(L.qp, xn, D, bq);
  qlin(L.kp, xn, D, bk);
  qlin(L.vp, xn, D, bv);

  conv4_silu(L.wt_q, st.hist[0][0], st.hist[0][1], st.hist[0][2], bq, cq, D);
  conv4_silu(L.wt_k, st.hist[1][0], st.hist[1][1], st.hist[1][2], bk, ck, D);
  conv4_silu(L.wt_v, st.hist[2][0], st.hist[2][1], st.hist[2][2], bv, cv, D);
  // shift conv histories (input of the conv, i.e. the projection outputs)
  const float* newest[3] = {bq, bk, bv};
  for (int c = 0; c < 3; c++) {
    std::memmove(st.hist[c][0], st.hist[c][1], sizeof(float) * 2 * D);
    std::memcpy(st.hist[c][2], newest[c], sizeof(float) * D);
  }
  capL(l, "kimi_conv_q", cq, D);
  capL(l, "kimi_conv_k", ck, D);
  capL(l, "kimi_conv_v", cv, D);

  qlin(L.fg_up, xn, D, fu);
  qlin(L.fg_down, fu, DH, graw);
  capL(l, "kimi_g_raw", graw, D);

  for (int h = 0; h < NH; h++)
    braw[h] = dot_f32(xn, L.beta_w + size_t(h) * D, D);
  capL(l, "kimi_beta_raw", braw, NH);

  qlin(L.og_up, xn, D, fu);
  qlin(L.og_down, fu, DH, og192);
  capL(l, "kimi_out_gate", og192, D);
  capL(l, "kimi_gate_in", og192, D);

  for (int h = 0; h < NH; h++)
    kda_head_step(st.S[h], cq + h * DH, ck + h * DH, cv + h * DH,
                  graw + h * DH, L.dt_bias + h * DH, L.a_neg[h],
                  sigmoid1f(braw[h]), o192 + h * DH);
  capL(l, "kimi_kda_out", o192, D);

  for (int h = 0; h < NH; h++)
    gated_rms_norm64(o192 + h * DH, og192 + h * DH, L.gn_w, gn + h * DH);
  capL(l, "kimi_gated_norm_out", gn, D);

  qlin(L.op, gn, D, y);
}

void TransformerImpl::van_attention(int vi, int l, const float* xn, float* y) {
  VanLayer& L = van[vi];
  VanState& st = vst[vi];
  alignas(32) float q[D], k[D], v[D], pre[D];
  alignas(32) int8_t qq[D], kk[D], vv[D];

  qlin(L.qp, xn, D, q);
  qlin(L.kp, xn, D, k);
  qlin(L.vp, xn, D, v);

  for (int h = 0; h < NH; h++) rms_norm_vec(q + h * DH, q + h * DH, DH);
  for (int h = 0; h < NH; h++) rms_norm_vec(k + h * DH, k + h * DH, DH);

  int64_t pos = rope_off + t;
  const float *sp, *cp;
  float sbuf[32], cbuf[32];
  if (pos < ROPE_LEN) {
    sp = rope_sin + size_t(pos) * 32;
    cp = rope_cos + size_t(pos) * 32;
  } else {
    float fpos = static_cast<float>(pos);
    for (int i = 0; i < 32; i++) {
      float ang = fpos * inv_freq[i];
      sbuf[i] = std::sin(ang);
      cbuf[i] = std::cos(ang);
    }
    sp = sbuf;
    cp = cbuf;
  }
  rope_apply(q, sp, cp);
  rope_apply(k, sp, cp);

  for (int h = 0; h < NH; h++) {
    quantize_i8(q + h * DH, DH, DH, L.sq[h], qq + h * DH);
    quantize_i8(k + h * DH, DH, DH, L.sk[h], kk + h * DH);
    quantize_i8(v + h * DH, DH, DH, L.sv[h], vv + h * DH);
  }
  if (cap_fn) {
    alignas(32) float fq[D];
    const struct {
      const char* quant;
      const char* ints;
      const int8_t* qv;
      const float* sc;
    } items[3] = {{"attn_q_quant", "attn_q_int8", qq, L.sq},
                  {"attn_k_quant", "attn_k_int8", kk, L.sk},
                  {"attn_v_quant", "attn_v_int8", vv, L.sv}};
    for (const auto& it : items) {
      for (int h = 0; h < NH; h++)
        for (int i = 0; i < DH; i++)
          fq[h * DH + i] =
              it.sc[h] * static_cast<float>(it.qv[h * DH + i]);
      capL(l, it.quant, fq, D);
      for (int i = 0; i < D; i++) fq[i] = static_cast<float>(it.qv[i]);
      capL(l, it.ints, fq, D);
    }
  }

  const int win_vi = attn_win::win(vi);  // this layer's window (attn_window.h)
  int slot = static_cast<int>(t % win_vi);
  std::memcpy(st.kring[slot], kk, D);
  std::memcpy(st.vring[slot], vv, D);

  float thr = lowprob_skip ? lowprob_threshold : 0.0f;
  int64_t n_valid = t + 1;
  if (n_valid < win_vi)
    attention_step_var(qq, st.kring[0], st.vring[0], L.coef, L.sv,
                       static_cast<int>(n_valid), pre, thr);
  else
    attention_step_fixed(qq, st.kring[0], st.vring[0], L.coef, L.sv, pre, thr, win_vi);
  capL(l, "attn_pre_oproj", pre, D);

  qlin(L.op, pre, D, y);
}

void TransformerImpl::step(uint8_t token, const float* prior,
                           float* probs_out) {
  if (token >= V) die("token out of range");
  const float* tok = tok_table + size_t(token) * D;
  float* x = xb;
  float* xn = xnb;

  // embedding path: x0 = normed token row + normed prior embedding
  qlin(prior_lin, prior, V, yb);
  rms_norm_vec(yb, yb, D);
  for (int i = 0; i < D; i++) x[i] = tok[i] + yb[i];
  cap("00_x0", x, D);

  for (int l = 0; l < NL; l++) {
    if (l >= NL - NSKIP) {  // skip connections: dest l <- source NL-1-l
      const float* s = skip_store[NL - 1 - l];
      float w = skip_w[l - (NL - NSKIP)];
      for (int i = 0; i < D; i++) x[i] += w * s[i];
    }
    if (override_fn) {  // debug teacher-forcing
      const float* forced = override_fn(l);
      if (forced) std::memcpy(x, forced, sizeof(float) * D);
    }
    capL(l, "block_input", x, D);

    {  // token-embedding connection
      float a = rsc[l], bcoef = tec[l];
      for (int i = 0; i < D; i++) x[i] = a * x[i] + bcoef * tok[i];
    }

    rms_norm_vec(x, xn, D);
    if (KIMI(l))
      kimi_attention(layer2kimi[l], l, xn, yb);
    else
      van_attention(layer2van[l], l, xn, yb);
    capL(l, "attn_out", yb, D);
    for (int i = 0; i < D; i++) x[i] += yb[i];

    rms_norm_vec(x, xn, D);
    const MlpW& m = mlp[l];
    qlin(m.up, xn, D, h768);
    for (int j = 0; j < DMLP; j++) {
      float hj = h768[j];
      h768[j] = hj > 0.0f ? hj * hj : 0.0f;  // relu^2
    }
    qlin(m.down, h768, DMLP, yb);
    capL(l, "mlp_out", yb, D);
    for (int i = 0; i < D; i++) x[i] += yb[i];
    capL(l, "block_output", x, D);

    if (l < NSKIP) std::memcpy(skip_store[l], x, sizeof(float) * D);
  }

  rms_norm_vec(x, xn, D);
  cap("12_final_norm", xn, D);
  qlin(unembed, xn, D, logits);
  for (int i = 0; i < V; i++)
    logits[i] = 15.0f * std::tanh(logits[i] / 15.0f);  // logit softcap
  cap("12_logits", logits, V);

  float m = logits[0];
  for (int i = 1; i < V; i++)
    if (logits[i] > m) m = logits[i];
  float den = 0.0f;
  for (int i = 0; i < V; i++) {
    float e = std::exp(logits[i] - m);
    probs_out[i] = e;
    den += e;
  }
  for (int i = 0; i < V; i++) probs_out[i] /= den;
  cap("12_probabilities", probs_out, V);

  t++;
}

Transformer::Transformer(const char* weights_path)
    : impl(new TransformerImpl()) {
  impl->load(weights_path);
}

Transformer::~Transformer() = default;

void Transformer::begin_article(int64_t rope_position_offset) {
  impl->begin(rope_position_offset);
}

void Transformer::step(uint8_t token, const uint16_t* prior_f16,
                       float* probs_out) {
  f16_to_f32(prior_f16, impl->prior_f32, V);
  for (int i = V; i < PRIOR_STRIDE; i++) impl->prior_f32[i] = 0.0f;
  impl->step(token, impl->prior_f32, probs_out);
}

void Transformer::step(uint8_t token, const float* prior205,
                       float* probs_out) {
  impl->step(token, prior205, probs_out);
}

const float* Transformer::last_logits() const { return impl->logits; }

void Transformer::set_attention_lowprob_skip(bool enabled, float threshold) {
  impl->lowprob_skip = enabled;
  impl->lowprob_threshold = threshold;
}

void Transformer::set_capture(CaptureFn fn) { impl->cap_fn = std::move(fn); }

void Transformer::set_block_input_override(BlockInputOverrideFn fn) {
  impl->override_fn = std::move(fn);
}

}  // namespace fx2
