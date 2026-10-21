// Exactness tests for the qmat kernels: every kernel's int32 dots must be
// bit-identical to a naive scalar reference, and every fused fp32/quantize
// epilogue must be bit-identical to the scalar single-rounding formulas
// (which themselves mirror src/kernels.cpp + model.cpp).
#include <immintrin.h>

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#include "../kernels.h"  // naive reference kernels (cross-check)
#include "qmat_dense.h"
#include "qmat_sparse.h"

using namespace fx2::opt;

static uint64_t g_rng = 0x243F6A8885A308D3ull;
static inline uint64_t rnd64() {
  g_rng ^= g_rng << 13;
  g_rng ^= g_rng >> 7;
  g_rng ^= g_rng << 17;
  return g_rng;
}
static inline int rndi(int lo, int hi) {  // inclusive
  return lo + static_cast<int>(rnd64() % static_cast<uint64_t>(hi - lo + 1));
}
static inline float rndf01() {
  return static_cast<float>(rnd64() >> 40) / static_cast<float>(1ull << 24);
}
// random fold scale: log-uniform magnitude, random sign, occasional zero
static inline float rnd_scale() {
  int r = rndi(0, 99);
  if (r < 2) return 0.0f;
  float mag = std::exp2f(-14.0f + 16.0f * rndf01());  // [2^-14, 4)
  return (rnd64() & 1) ? mag : -mag;
}

static int g_fail = 0;
#define CHECK(cond, ...)                                        \
  do {                                                          \
    if (!(cond)) {                                              \
      std::printf("FAIL %s:%d: ", __FILE__, __LINE__);          \
      std::printf(__VA_ARGS__);                                 \
      std::printf("\n");                                        \
      if (++g_fail > 20) std::exit(1);                          \
    }                                                           \
  } while (0)

static inline bool bit_eq(float a, float b) {
  uint32_t x, y;
  std::memcpy(&x, &a, 4);
  std::memcpy(&y, &b, 4);
  return x == y;
}
static inline int round_half_even(float t) {  // matches naive scalar tail
  return _mm_cvtss_si32(_mm_set_ss(t));
}
// TF_ACTQ_DYN reference: s = max(amax, 1e-12f) / 127.0f (pysrc/quantization.py dynamic branch)
static inline float ref_dyn_scale(float amax) {
  if (amax < 1e-12f) amax = 1e-12f;
  return amax / 127.0f;
}

// scalar int32 dots on the SIGNED ints (the ground truth)
static void ref_dots(const int8_t* qw, int d_out, int d_in, const int* qa,
                     int32_t* dot) {
  for (int o = 0; o < d_out; o++) {
    int64_t s = 0;
    for (int i = 0; i < d_in; i++)
      s += static_cast<int64_t>(qa[i]) * qw[static_cast<size_t>(o) * d_in + i];
    dot[o] = static_cast<int32_t>(s);
  }
}

struct Buf {
  std::vector<uint8_t> v;
  uint8_t* p;
  explicit Buf(size_t n) : v(n + 128 + QMAT_TAIL_SLACK, 0) {
    p = reinterpret_cast<uint8_t*>(
        (reinterpret_cast<uintptr_t>(v.data()) + 63) & ~uintptr_t(63));
  }
};

// ---------------------------------------------------------------------------
// dense tests for one shape
// ---------------------------------------------------------------------------
static void test_dense_shape(int d_out, int d_in, bool biased, int cases,
                             bool directed_ties) {
  const int rows_pad = qmat_round_up(d_out, qmat_group_rows(d_in));
  const int stride = qmat_round_up(d_in, 32);
  std::vector<int8_t> qw(static_cast<size_t>(d_out) * d_in);
  std::vector<float> fold(d_out);
  std::vector<int> qa(d_in);
  alignas(64) static uint8_t act[768];
  std::vector<int32_t> dref(rows_pad), dgot(rows_pad);
  std::vector<float> fgot(rows_pad), fref(rows_pad), res0(rows_pad);
  Buf arena(qdense_bytes(d_out, d_in));

  const bool do_c = (d_in == 192 && d_out == 768);
  const bool do_d = (d_in == 192 && d_out == 64);
  std::vector<uint8_t> qc_got(rows_pad), qc_ref(rows_pad);
  std::vector<uint16_t> idx_got(rows_pad + 8), idx_ref(rows_pad);

  for (int cs = 0; cs < cases; cs++) {
    const bool extreme = cs % 37 == 0;  // saturation-bound patterns
    for (size_t i = 0; i < qw.size(); i++)
      qw[i] = static_cast<int8_t>(extreme ? (rnd64() & 1 ? QMAT_WMAX : -QMAT_WMAX)
                                          : rndi(-QMAT_WMAX, QMAT_WMAX));
    for (int o = 0; o < d_out; o++)
      fold[o] = directed_ties ? 1.0f : rnd_scale();
    std::memset(act, 0, sizeof(act));
    for (int i = 0; i < d_in; i++) {
      if (biased) {
        qa[i] = extreme ? (rnd64() & 1 ? 127 : -128) : rndi(-128, 127);
        act[i] = static_cast<uint8_t>(qa[i] + 128);
      } else {
        qa[i] = extreme ? (rnd64() & 1 ? 127 : 0) : rndi(0, 127);
        act[i] = static_cast<uint8_t>(qa[i]);
      }
    }
    QDense m = qdense_build(arena.p, qw.data(), fold.data(), d_out, d_in,
                            biased);

    // int32 dots
    ref_dots(qw.data(), d_out, d_in, qa.data(), dref.data());
    for (int o = d_out; o < rows_pad; o++) dref[o] = 0;
    qgemv_i32(m, act, dgot.data());
    for (int o = 0; o < rows_pad; o++)
      CHECK(dgot[o] == dref[o], "i32 %dx%d case %d row %d: got %d want %d",
            d_out, d_in, cs, o, dgot[o], dref[o]);

    // (a) f32 store
    qgemv_f32(m, act, fgot.data());
    for (int o = 0; o < rows_pad; o++) {
      float scl = o < d_out ? fold[o] : 0.0f;
      float want = scl * static_cast<float>(dref[o]);
      CHECK(bit_eq(fgot[o], want), "f32 %dx%d case %d row %d: %a want %a",
            d_out, d_in, cs, o, fgot[o], want);
    }
    if (cs % 3 == 0) {  // prefetch-off variant must be identical
      qgemv_f32_nopf(m, act, fref.data());
      for (int o = 0; o < rows_pad; o++)
        CHECK(bit_eq(fref[o], fgot[o]), "f32_nopf mismatch row %d", o);
    }

    // (b) residual add: res + (scl*float(dot)), mul rounded then add rounded
    for (int o = 0; o < rows_pad; o++) {
      res0[o] = (rndf01() - 0.5f) * 8.0f;
      fgot[o] = res0[o];
    }
    qgemv_add(m, act, fgot.data());
    for (int o = 0; o < rows_pad; o++) {
      float scl = o < d_out ? fold[o] : 0.0f;
      float t = scl * static_cast<float>(dref[o]);
      float want = res0[o] + t;
      CHECK(bit_eq(fgot[o], want), "add %dx%d case %d row %d: %a want %a",
            d_out, d_in, cs, o, fgot[o], want);
    }

    // (e)/(f) TF_ACTQ_DYN scaled epilogues: (scl*float(dot))*s, then store / add
    {
      const float s_tok = std::exp2f(-12.0f + 14.0f * rndf01());
      qgemv_f32s(m, act, s_tok, fgot.data());
      for (int o = 0; o < rows_pad; o++) {
        float scl = o < d_out ? fold[o] : 0.0f;
        float want = (scl * static_cast<float>(dref[o])) * s_tok;
        CHECK(bit_eq(fgot[o], want), "f32s %dx%d case %d row %d: %a want %a",
              d_out, d_in, cs, o, fgot[o], want);
      }
      for (int o = 0; o < rows_pad; o++) fgot[o] = res0[o];
      qgemv_adds(m, act, s_tok, fgot.data());
      for (int o = 0; o < rows_pad; o++) {
        float scl = o < d_out ? fold[o] : 0.0f;
        float t = (scl * static_cast<float>(dref[o])) * s_tok;
        float want = res0[o] + t;
        CHECK(bit_eq(fgot[o], want), "adds %dx%d case %d row %d: %a want %a",
              d_out, d_in, cs, o, fgot[o], want);
      }
    }

    // (c) relu^2 + quantize + index list (mlp.up shape)
    if (do_c) {
      float s_next = directed_ties ? 2.0f : std::exp2f(-8.0f + 10.0f * rndf01());
      std::memset(idx_got.data(), 0, idx_got.size() * 2);
      int nnz = qgemv_relu2q(m, act, s_next, qc_got.data(), idx_got.data());
      int nref = 0;
      for (int o = 0; o < d_out; o++) {
        float y = fold[o] * static_cast<float>(dref[o]);
        float h = y > 0.0f ? y * y : 0.0f;
        float t = h / s_next;
        if (t > 127.0f) t = 127.0f;
        int q = round_half_even(t);
        qc_ref[o] = static_cast<uint8_t>(q);
        if (q != 0) idx_ref[nref++] = static_cast<uint16_t>(o);
      }
      CHECK(nnz == nref, "relu2q nnz case %d: got %d want %d", cs, nnz, nref);
      for (int o = 0; o < d_out; o++)
        CHECK(qc_got[o] == qc_ref[o], "relu2q q case %d row %d: %d want %d",
              cs, o, qc_got[o], qc_ref[o]);
      for (int k = 0; k < nref; k++)
        CHECK(idx_got[k] == idx_ref[k], "relu2q idx case %d k %d: %d want %d",
              cs, k, idx_got[k], idx_ref[k]);
      for (int k = nref; k < nref + 8; k++)  // slack entries stay in range
        CHECK(idx_got[k] < rows_pad, "relu2q idx slack out of range");
      // cross-check against the naive kernel chain (qmatvec -> relu^2 ->
      // quantize_i8), which is the actual model reference path
      if (cs % 7 == 0) {
        std::vector<int8_t> wpad(static_cast<size_t>(d_out) * stride, 0);
        std::vector<int8_t> apad(stride, 0), qn(d_out);
        std::vector<float> yv(d_out);
        for (int o = 0; o < d_out; o++)
          std::memcpy(&wpad[static_cast<size_t>(o) * stride],
                      &qw[static_cast<size_t>(o) * d_in], d_in);
        for (int i = 0; i < d_in; i++) apad[i] = static_cast<int8_t>(qa[i]);
        fx2::qmatvec(wpad.data(), stride, fold.data(), d_out, apad.data(),
                     yv.data());
        for (int o = 0; o < d_out; o++) {
          float h = yv[o] > 0.0f ? yv[o] * yv[o] : 0.0f;
          yv[o] = h;
        }
        fx2::quantize_i8(yv.data(), d_out, d_out, s_next, qn.data());
        for (int o = 0; o < d_out; o++)
          CHECK(static_cast<uint8_t>(qn[o]) == qc_got[o],
                "relu2q vs naive chain case %d row %d", cs, o);
      }
    }

    // (g) TF_ACTQ_DYN mlp.up: relu^2 of the token-scaled output, DYNAMIC scale of h, quantize + index list
    if (do_c) {
      const float s_in = directed_ties ? 0.5f : std::exp2f(-12.0f + 14.0f * rndf01());
      std::memset(idx_got.data(), 0, idx_got.size() * 2);
      float s_h_got = -1.0f;
      int nnz = qgemv_relu2q_dyn(m, act, s_in, qc_got.data(), idx_got.data(), &s_h_got);
      std::vector<float> h(d_out);
      float amax = 0.0f;
      for (int o = 0; o < d_out; o++) {
        float y = (fold[o] * static_cast<float>(dref[o])) * s_in;
        h[o] = y > 0.0f ? y * y : 0.0f;
        if (h[o] > amax) amax = h[o];
      }
      const float s_h = ref_dyn_scale(amax);
      CHECK(bit_eq(s_h_got, s_h), "relu2q_dyn s_h case %d: %a want %a", cs, s_h_got, s_h);
      int nref = 0;
      for (int o = 0; o < d_out; o++) {
        float t = h[o] / s_h;
        if (t > 127.0f) t = 127.0f;
        int q = round_half_even(t);
        qc_ref[o] = static_cast<uint8_t>(q);
        if (q != 0) idx_ref[nref++] = static_cast<uint16_t>(o);
      }
      CHECK(nnz == nref, "relu2q_dyn nnz case %d: got %d want %d", cs, nnz, nref);
      for (int o = 0; o < d_out; o++)
        CHECK(qc_got[o] == qc_ref[o], "relu2q_dyn q case %d row %d: %d want %d", cs, o, qc_got[o], qc_ref[o]);
      for (int k = 0; k < nref; k++)
        CHECK(idx_got[k] == idx_ref[k], "relu2q_dyn idx case %d k %d: %d want %d", cs, k, idx_got[k], idx_ref[k]);
      for (int k = nref; k < nref + 8; k++) CHECK(idx_got[k] < rows_pad, "relu2q_dyn idx slack out of range");
      // the max element quantizes to 127 whenever h is not all zero
      if (amax > 0.0f) {
        int qmax = 0;
        for (int o = 0; o < d_out; o++) qmax = qc_got[o] > qmax ? qc_got[o] : qmax;
        CHECK(qmax == 127, "relu2q_dyn max lane case %d: %d", cs, qmax);
      }
      // cross-check against the naive chain: qmatvec -> scale_vec -> relu^2 -> dyn_act_scale -> quantize_i8
      if (cs % 7 == 0) {
        std::vector<int8_t> wpad(static_cast<size_t>(d_out) * stride, 0);
        std::vector<int8_t> apad(stride, 0), qn(d_out);
        std::vector<float> yv(d_out);
        for (int o = 0; o < d_out; o++)
          std::memcpy(&wpad[static_cast<size_t>(o) * stride], &qw[static_cast<size_t>(o) * d_in], d_in);
        for (int i = 0; i < d_in; i++) apad[i] = static_cast<int8_t>(qa[i]);
        fx2::qmatvec(wpad.data(), stride, fold.data(), d_out, apad.data(), yv.data());
        fx2::scale_vec(yv.data(), d_out, s_in);
        for (int o = 0; o < d_out; o++) yv[o] = yv[o] > 0.0f ? yv[o] * yv[o] : 0.0f;
        const float sn = fx2::dyn_act_scale(yv.data(), d_out);
        CHECK(bit_eq(sn, s_h_got), "relu2q_dyn vs naive dyn_act_scale case %d", cs);
        fx2::quantize_i8(yv.data(), d_out, d_out, sn, qn.data());
        for (int o = 0; o < d_out; o++)
          CHECK(static_cast<uint8_t>(qn[o]) == qc_got[o], "relu2q_dyn vs naive chain case %d row %d", cs, o);
      }
    }

    // (d) quantize + bias 128 (gate-chain shape)
    if (do_d) {
      float s_next = directed_ties ? 2.0f : std::exp2f(-8.0f + 10.0f * rndf01());
      qgemv_quant_bias(m, act, s_next, qc_got.data());
      for (int o = 0; o < d_out; o++) {
        float y = fold[o] * static_cast<float>(dref[o]);
        float t = y / s_next;
        t = t < -128.0f ? -128.0f : (t > 127.0f ? 127.0f : t);
        int q = round_half_even(t);
        CHECK(qc_got[o] == static_cast<uint8_t>(q + 128),
              "quant_bias case %d row %d: %d want %d", cs, o, qc_got[o],
              q + 128);
      }
      // (h) TF_ACTQ_DYN gate chain: token-scaled output, DYNAMIC scale of the 64-dim intermediate
      const float s_in = directed_ties ? 0.5f : std::exp2f(-12.0f + 14.0f * rndf01());
      const float s_y_got = qgemv_quant_bias_dyn(m, act, s_in, qc_got.data());
      std::vector<float> yv(d_out);
      float amax = 0.0f;
      for (int o = 0; o < d_out; o++) {
        yv[o] = (fold[o] * static_cast<float>(dref[o])) * s_in;
        const float a = std::fabs(yv[o]);
        if (a > amax) amax = a;
      }
      const float s_y = ref_dyn_scale(amax);
      CHECK(bit_eq(s_y_got, s_y), "quant_bias_dyn s_y case %d: %a want %a", cs, s_y_got, s_y);
      CHECK(bit_eq(s_y_got, fx2::dyn_act_scale(yv.data(), d_out)), "quant_bias_dyn vs naive dyn_act_scale case %d", cs);
      for (int o = 0; o < d_out; o++) {
        float t = yv[o] / s_y;
        t = t < -128.0f ? -128.0f : (t > 127.0f ? 127.0f : t);
        int q = round_half_even(t);
        CHECK(qc_got[o] == static_cast<uint8_t>(q + 128), "quant_bias_dyn case %d row %d: %d want %d", cs, o,
              qc_got[o], q + 128);
      }
    }
  }
  std::printf("ok dense %dx%d %s (%d cases%s%s%s)\n", d_out, d_in,
              biased ? "biased" : "raw", cases, do_c ? " +relu2q(+dyn) +f32s/adds" : " +f32s/adds",
              do_d ? " +quant_bias(+dyn)" : "", directed_ties ? " ties" : "");
}

// naive qmatvec must agree bitwise with qgemv_f32 (same formula)
static void test_vs_naive_qmatvec(int d_out, int d_in, int cases) {
  const int stride = (d_in + 15) & ~15;
  std::vector<int8_t> qw(static_cast<size_t>(d_out) * d_in);
  std::vector<int8_t> wpad(static_cast<size_t>(d_out) * stride, 0);
  std::vector<int8_t> apad(stride, 0);
  std::vector<float> fold(d_out), ynaive(d_out);
  std::vector<int> qa(d_in);
  alignas(64) static uint8_t act[768];
  const int rows_pad = qmat_round_up(d_out, qmat_group_rows(d_in));
  std::vector<float> fgot(rows_pad);
  Buf arena(qdense_bytes(d_out, d_in));
  for (int cs = 0; cs < cases; cs++) {
    for (size_t i = 0; i < qw.size(); i++) qw[i] = static_cast<int8_t>(rndi(-QMAT_WMAX, QMAT_WMAX));
    for (int o = 0; o < d_out; o++) fold[o] = rnd_scale();
    std::memset(act, 0, sizeof(act));
    for (int i = 0; i < d_in; i++) {
      qa[i] = rndi(-128, 127);
      act[i] = static_cast<uint8_t>(qa[i] + 128);
      apad[i] = static_cast<int8_t>(qa[i]);
    }
    for (int o = 0; o < d_out; o++)
      std::memcpy(&wpad[static_cast<size_t>(o) * stride],
                  &qw[static_cast<size_t>(o) * d_in], d_in);
    QDense m = qdense_build(arena.p, qw.data(), fold.data(), d_out, d_in, true);
    qgemv_f32(m, act, fgot.data());
    fx2::qmatvec(wpad.data(), stride, fold.data(), d_out, apad.data(),
                 ynaive.data());
    for (int o = 0; o < d_out; o++)
      CHECK(bit_eq(fgot[o], ynaive[o]), "vs naive %dx%d case %d row %d",
            d_out, d_in, cs, o);
  }
  std::printf("ok dense-vs-naive-qmatvec %dx%d (%d cases)\n", d_out, d_in,
              cases);
}

// ---------------------------------------------------------------------------
// sparse tests (d_out = 192)
// ---------------------------------------------------------------------------
static void test_sparse_shape(int d_in, int cases) {
  std::vector<int8_t> qw(static_cast<size_t>(192) * d_in);
  std::vector<float> fold(192);
  std::vector<int> qa(d_in);
  std::vector<uint8_t> q8(qmat_round_up(d_in, 32), 0);
  std::vector<uint16_t> idx(d_in + 16, 0);
  std::vector<int32_t> dref(192), dgot(192);
  std::vector<float> fgot(192), res0(192);
  Buf colbuf(qsparse_bytes(d_in));
  alignas(64) static float foldbuf[192];

  std::vector<int8_t> qidx(qw.size());  // level indices for the nibble arena (codebook build)
  int8_t cb[16] = {0};
  for (int cs = 0; cs < cases; cs++) {
#if QMAT_CODEBOOK
    // random codebook (extreme cases: all +-QMAT_WMAX, the exact int16 bound of the flush cadence)
    for (int k = 0; k < 15; k++) cb[k] = static_cast<int8_t>(cs % 29 == 0 ? (k & 1 ? QMAT_WMAX : -QMAT_WMAX) : rndi(-QMAT_WMAX, QMAT_WMAX));
    cb[15] = 0;
    for (size_t i = 0; i < qw.size(); i++) { qidx[i] = static_cast<int8_t>(rndi(-7, 7)); qw[i] = cb[qidx[i] + 7]; }
#else
    for (size_t i = 0; i < qw.size(); i++) qw[i] = static_cast<int8_t>(rndi(-7, 7));
    qidx = qw;
#endif
    for (int o = 0; o < 192; o++) fold[o] = rnd_scale();
    // density: sweep the whole range incl. empty / full / odd nnz
    float dens = cs % 17 == 0 ? 0.0f : (cs % 13 == 0 ? 1.0f : rndf01());
    const bool extreme = cs % 29 == 0;
    int nnz = 0;
    std::fill(q8.begin(), q8.end(), 0);
    for (int i = 0; i < d_in; i++) {
      if (rndf01() < dens) {
        qa[i] = extreme ? 127 : rndi(1, 127);
        q8[i] = static_cast<uint8_t>(qa[i]);
        idx[nnz++] = static_cast<uint16_t>(i);
      } else {
        qa[i] = 0;
      }
    }
    for (int k = nnz; k < nnz + 8; k++) idx[k] = idx[nnz ? nnz - 1 : 0];
    QSparse m = qsparse_build(reinterpret_cast<int8_t*>(colbuf.p), foldbuf,
                              qw.data(), fold.data(), 192, d_in);

    ref_dots(qw.data(), 192, d_in, qa.data(), dref.data());

    qsparse_i32(m, q8.data(), idx.data(), nnz, dgot.data());
    for (int o = 0; o < 192; o++)
      CHECK(dgot[o] == dref[o], "sp i32 din=%d case %d row %d: %d want %d",
            d_in, cs, o, dgot[o], dref[o]);

    qsparse_f32(m, q8.data(), idx.data(), nnz, fgot.data());
    for (int o = 0; o < 192; o++) {
      float want = foldbuf[o] * static_cast<float>(dref[o]);
      CHECK(bit_eq(fgot[o], want), "sp f32 din=%d case %d row %d", d_in, cs, o);
    }
    if (cs % 3 == 0) {
      std::vector<float> f2(192);
      qsparse_f32_nopf(m, q8.data(), idx.data(), nnz, f2.data());
      for (int o = 0; o < 192; o++)
        CHECK(bit_eq(f2[o], fgot[o]), "sp f32_nopf mismatch row %d", o);
    }

    for (int o = 0; o < 192; o++) {
      res0[o] = (rndf01() - 0.5f) * 8.0f;
      fgot[o] = res0[o];
    }
    qsparse_add(m, q8.data(), idx.data(), nnz, fgot.data());
    for (int o = 0; o < 192; o++) {
      float t = foldbuf[o] * static_cast<float>(dref[o]);
      float want = res0[o] + t;
      CHECK(bit_eq(fgot[o], want), "sp add din=%d case %d row %d", d_in, cs, o);
    }

    // dense-over-columns fallback: identical results
    qsparse_dense_i32(m, q8.data(), dgot.data());
    for (int o = 0; o < 192; o++)
      CHECK(dgot[o] == dref[o], "sp dense i32 din=%d case %d row %d", d_in, cs,
            o);
    qsparse_dense_f32(m, q8.data(), fgot.data());
    for (int o = 0; o < 192; o++) {
      float want = foldbuf[o] * static_cast<float>(dref[o]);
      CHECK(bit_eq(fgot[o], want), "sp dense f32 din=%d case %d row %d", d_in,
            cs, o);
    }
    for (int o = 0; o < 192; o++) fgot[o] = res0[o];
    qsparse_dense_add(m, q8.data(), fgot.data());
    for (int o = 0; o < 192; o++) {
      float t = foldbuf[o] * static_cast<float>(dref[o]);
      CHECK(bit_eq(fgot[o], res0[o] + t), "sp dense add din=%d row %d", d_in, o);
    }

    // index-list builder
    std::vector<uint16_t> idx2(d_in + 16, 0);
    int n2 = qsparse_make_idx(q8.data(), d_in, idx2.data());
    CHECK(n2 == nnz, "make_idx nnz din=%d case %d: %d want %d", d_in, cs, n2,
          nnz);
    for (int k = 0; k < nnz; k++)
      CHECK(idx2[k] == idx[k], "make_idx din=%d case %d k %d", d_in, cs, k);

    // int4-packed column kernels: identical results
    static Buf col4buf(qsparse4_bytes(768));
    alignas(64) static float fold4buf[192];
    QSparse4 m4 = qsparse4_build(col4buf.p, fold4buf, qidx.data(), fold.data(),
                                 192, d_in);
#if QMAT_CODEBOOK
    for (int k = 0; k < 16; k++) m4.lut[k] = m4.lut[16 + k] = cb[k];
#endif
    qsparse4_i32(m4, q8.data(), idx.data(), nnz, dgot.data());
    for (int o = 0; o < 192; o++)
      CHECK(dgot[o] == dref[o], "sp4 i32 din=%d case %d row %d: %d want %d",
            d_in, cs, o, dgot[o], dref[o]);
    qsparse4_f32(m4, q8.data(), idx.data(), nnz, fgot.data());
    for (int o = 0; o < 192; o++) {
      float want = fold4buf[o] * static_cast<float>(dref[o]);
      CHECK(bit_eq(fgot[o], want), "sp4 f32 din=%d case %d row %d", d_in, cs,
            o);
    }
    for (int o = 0; o < 192; o++) fgot[o] = res0[o];
    qsparse4_add(m4, q8.data(), idx.data(), nnz, fgot.data());
    for (int o = 0; o < 192; o++) {
      float t = fold4buf[o] * static_cast<float>(dref[o]);
      CHECK(bit_eq(fgot[o], res0[o] + t), "sp4 add din=%d case %d row %d",
            d_in, cs, o);
    }
    qsparse4_dense_i32(m4, q8.data(), dgot.data());
    for (int o = 0; o < 192; o++)
      CHECK(dgot[o] == dref[o], "sp4 dense i32 din=%d case %d row %d", d_in,
            cs, o);
    qsparse4_dense_f32(m4, q8.data(), fgot.data());
    for (int o = 0; o < 192; o++) {
      float want = fold4buf[o] * static_cast<float>(dref[o]);
      CHECK(bit_eq(fgot[o], want), "sp4 dense f32 din=%d case %d row %d", d_in,
            cs, o);
    }
    for (int o = 0; o < 192; o++) fgot[o] = res0[o];
    qsparse4_dense_add(m4, q8.data(), fgot.data());
    for (int o = 0; o < 192; o++) {
      float t = fold4buf[o] * static_cast<float>(dref[o]);
      CHECK(bit_eq(fgot[o], res0[o] + t), "sp4 dense add din=%d row %d", d_in,
            o);
    }
    // TF_ACTQ_DYN scaled epilogues: (fold*float(dot))*s, then store / add
    {
      const float s_tok = std::exp2f(-12.0f + 14.0f * rndf01());
      qsparse4_f32s(m4, q8.data(), idx.data(), nnz, s_tok, fgot.data());
      for (int o = 0; o < 192; o++) {
        float want = (fold4buf[o] * static_cast<float>(dref[o])) * s_tok;
        CHECK(bit_eq(fgot[o], want), "sp4 f32s din=%d case %d row %d", d_in, cs, o);
      }
      for (int o = 0; o < 192; o++) fgot[o] = res0[o];
      qsparse4_adds(m4, q8.data(), idx.data(), nnz, s_tok, fgot.data());
      for (int o = 0; o < 192; o++) {
        float t = (fold4buf[o] * static_cast<float>(dref[o])) * s_tok;
        CHECK(bit_eq(fgot[o], res0[o] + t), "sp4 adds din=%d case %d row %d", d_in, cs, o);
      }
      qsparse4_dense_f32s(m4, q8.data(), s_tok, fgot.data());
      for (int o = 0; o < 192; o++) {
        float want = (fold4buf[o] * static_cast<float>(dref[o])) * s_tok;
        CHECK(bit_eq(fgot[o], want), "sp4 dense f32s din=%d case %d row %d", d_in, cs, o);
      }
      for (int o = 0; o < 192; o++) fgot[o] = res0[o];
      qsparse4_dense_adds(m4, q8.data(), s_tok, fgot.data());
      for (int o = 0; o < 192; o++) {
        float t = (fold4buf[o] * static_cast<float>(dref[o])) * s_tok;
        CHECK(bit_eq(fgot[o], res0[o] + t), "sp4 dense adds din=%d case %d row %d", d_in, cs, o);
      }
    }
  }
  std::printf("ok sparse 192x%d incl. int4 columns (%d cases)\n", d_in, cases);
}

// ---------------------------------------------------------------------------
// packed int4 tests
// ---------------------------------------------------------------------------
static void test_packed_shape(int d_out, int d_in, bool raw_acts, int cases) {
  const int rows_pad = qmat_round_up(d_out, 4);
  const int stride4 = qmat_round_up(d_in, 64);
  std::vector<int8_t> qw(static_cast<size_t>(d_out) * d_in);
  std::vector<float> fold(d_out);
  std::vector<int> qa(d_in);
  alignas(64) static int8_t act[768];
  std::vector<int32_t> dref(rows_pad), dgot(rows_pad);
  std::vector<float> fgot(rows_pad);
  Buf arena(qpacked_bytes(d_out, d_in));
  for (int cs = 0; cs < cases; cs++) {
    for (size_t i = 0; i < qw.size(); i++) qw[i] = static_cast<int8_t>(rndi(-7, 7));
    for (int o = 0; o < d_out; o++) fold[o] = rnd_scale();
    std::memset(act, 0, sizeof(act));
    int32_t sum = 0;
    for (int i = 0; i < d_in; i++) {
      qa[i] = raw_acts ? rndi(0, 127) : rndi(-128, 127);
      act[i] = static_cast<int8_t>(qa[i]);
      sum += qa[i];
    }
    QPacked m = qpacked_build(arena.p, qw.data(), fold.data(), d_out, d_in);
    (void)stride4;
    ref_dots(qw.data(), d_out, d_in, qa.data(), dref.data());
    for (int o = d_out; o < rows_pad; o++) dref[o] = 0;
    qgemv_packed_i32(m, act, 7 * sum, dgot.data());
    for (int o = 0; o < rows_pad; o++)
      CHECK(dgot[o] == dref[o], "p4 i32 %dx%d case %d row %d: %d want %d",
            d_out, d_in, cs, o, dgot[o], dref[o]);
    qgemv_packed_f32(m, act, 7 * sum, fgot.data());
    for (int o = 0; o < rows_pad; o++) {
      float scl = o < d_out ? fold[o] : 0.0f;
      float want = scl * static_cast<float>(dref[o]);
      CHECK(bit_eq(fgot[o], want), "p4 f32 %dx%d case %d row %d", d_out, d_in,
            cs, o);
    }
  }
  std::printf("ok packed %dx%d %s (%d cases)\n", d_out, d_in,
              raw_acts ? "raw" : "signed", cases);
}

// ---------------------------------------------------------------------------
// 8-bit small matmuls (QW8, qmat.h): exact vs the scalar signed dot for the
// prior (192x205, raw acts in [0,127], corr 0) and unembedding (205x192,
// biased acts qa+128, corr 128*sum w) shapes, weights in [-127,127]
// ---------------------------------------------------------------------------
static void test_qw8_shape(int d_out, int d_in, bool biased, int cases) {
  const int stride = qmat_round_up(d_in, 32), rows_pad = qmat_round_up(d_out, 8);
  std::vector<int8_t> qw(static_cast<size_t>(d_out) * d_in);
  std::vector<float> fold(d_out), fgot(rows_pad);
  std::vector<int> qa(d_in);
  std::vector<int32_t> dref(d_out);
  alignas(64) static uint8_t act[768];
  Buf wbuf(qw8_bytes(d_out, d_in));
  alignas(64) static int32_t corr[256];
  alignas(64) static float fld[256];
  for (int cs = 0; cs < cases; cs++) {
    const bool extreme = cs % 31 == 0;
    for (size_t i = 0; i < qw.size(); i++)
      qw[i] = static_cast<int8_t>(extreme ? (rnd64() & 1 ? 127 : -127) : rndi(-127, 127));
    for (int o = 0; o < d_out; o++) fold[o] = rnd_scale();
    std::memset(act, 0, sizeof(act));
    for (int i = 0; i < d_in; i++) {
      if (biased) { qa[i] = extreme ? (rnd64() & 1 ? 127 : -128) : rndi(-128, 127); act[i] = static_cast<uint8_t>(qa[i] + 128); }
      else { qa[i] = extreme ? 127 : rndi(0, 127); act[i] = static_cast<uint8_t>(qa[i]); }
    }
    QW8 m = qw8_build(reinterpret_cast<int8_t*>(wbuf.p), corr, fld, qw.data(), fold.data(), d_out, d_in, biased);
    ref_dots(qw.data(), d_out, d_in, qa.data(), dref.data());
    qw8_f32(m, act, fgot.data());
    for (int o = 0; o < d_out; o++) {
      const float want = fold[o] * static_cast<float>(dref[o]);
      CHECK(bit_eq(fgot[o], want), "qw8 %dx%d case %d row %d: %g want %g", d_out, d_in, cs, o, fgot[o], want);
    }
    for (int o = d_out; o < rows_pad; o++) CHECK(fgot[o] == 0.0f, "qw8 pad row %d not zero", o);
  }
  (void)stride;
  std::printf("ok qw8 %dx%d %s (%d cases)\n", d_out, d_in, biased ? "biased" : "raw", cases);
}

int main(int argc, char** argv) {
  int N = argc > 1 ? std::atoi(argv[1]) : 10000;
  test_qw8_shape(192, 205, false, N);   // 8-bit prior projection
  test_qw8_shape(205, 192, true, N);    // 8-bit unembedding
  int Nbig = N;  // big shapes too: full case count (scalar ref is fast enough)

  // the five dense production shapes (d_out x d_in)
  test_dense_shape(192, 192, true, N, false);
  test_dense_shape(768, 192, true, Nbig, false);   // + relu2q epilogue
  test_dense_shape(64, 192, true, N, false);       // + quant_bias epilogue
  test_dense_shape(192, 64, true, N, false);
  test_dense_shape(205, 192, true, Nbig, false);   // unembedding (row pad)
  // raw-u8 (corr = 0) dense arenas: prior (in-dim pad) and mlp.down fallback
  test_dense_shape(192, 205, false, Nbig, false);
  test_dense_shape(192, 768, false, Nbig, false);
  test_dense_shape(192, 768, true, Nbig, false);   // biased 768-in for coverage
  // directed rounding-tie cases for the quantizing epilogues (fold=1, s=2)
  test_dense_shape(768, 192, true, 400, true);
  test_dense_shape(64, 192, true, 400, true);

  test_vs_naive_qmatvec(192, 192, 2000);
  test_vs_naive_qmatvec(768, 192, 500);

  test_sparse_shape(768, Nbig);
  test_sparse_shape(205, N);

  test_packed_shape(192, 192, false, Nbig);
  test_packed_shape(768, 192, false, Nbig / 2);
  test_packed_shape(64, 192, false, Nbig);
  test_packed_shape(192, 64, false, Nbig);
  test_packed_shape(205, 192, false, Nbig / 2);
  test_packed_shape(192, 205, false, Nbig / 2);
  test_packed_shape(192, 768, true, Nbig / 2);

  if (g_fail == 0) {
    std::printf("ALL EXACTNESS TESTS PASSED\n");
    return 0;
  }
  std::printf("FAILURES: %d\n", g_fail);
  return 1;
}
