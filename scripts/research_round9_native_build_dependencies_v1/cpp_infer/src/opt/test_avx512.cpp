// test_avx512.cpp -- AVX2 vs AVX-512 kernel equality (TF_AVX512 fast path): every kernel of
// qmat_avx512.h is run against its AVX2 twin (qmat_dense.h / qmat_sparse.h) on many random inputs
// (incl. extreme codebook / int8 / activation values) and every output is compared BITWISE (int32
// dots, fp32 outputs, quantized u8 vectors, index lists, dynamic scales). The int32 dots are also
// checked against the scalar int64 reference. The QPackedCB arena (qmat.h section 4) is checked
// against the AVX2 QDense kernels on the same logical weights (random codebooks in the QMAT_CODEBOOK
// build, no assumption on the zero level). Build with -DTF_AVX512=1 -DQMAT_AVX512_ALL_SHAPES=1
// (src/opt/Makefile test_avx512); needs an AVX-512 VNNI host (exit 2 = SKIP otherwise).
#include <immintrin.h>

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <algorithm>
#include <vector>

#include "qmat_avx512.h"
#include "qmat_cpu.h"
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
static inline int rndi(int lo, int hi) { return lo + static_cast<int>(rnd64() % static_cast<uint64_t>(hi - lo + 1)); }
static inline float rndf01() { return static_cast<float>(rnd64() >> 40) / static_cast<float>(1ull << 24); }
static inline float rnd_scale() {
  int r = rndi(0, 99);
  if (r < 2) return 0.0f;
  float mag = std::exp2f(-14.0f + 16.0f * rndf01());
  return (rnd64() & 1) ? mag : -mag;
}
static inline float rnd_pos_scale() { return std::exp2f(-12.0f + 10.0f * rndf01()); }

static long g_fail = 0, g_checks = 0;
#define CHECK(cond, ...)                                       \
  do {                                                         \
    g_checks++;                                                \
    if (!(cond)) {                                             \
      std::printf("FAIL %s:%d: ", __FILE__, __LINE__);         \
      std::printf(__VA_ARGS__);                                \
      std::printf("\n");                                       \
      if (++g_fail > 30) std::exit(1);                         \
    }                                                          \
  } while (0)

static inline bool bit_eq(float a, float b) {
  uint32_t x, y;
  std::memcpy(&x, &a, 4);
  std::memcpy(&y, &b, 4);
  return x == y;
}
static bool bits_eq(const float* a, const float* b, int n, int* first) {
  for (int i = 0; i < n; i++)
    if (!bit_eq(a[i], b[i])) { *first = i; return false; }
  return true;
}

struct Buf {
  std::vector<uint8_t> v;
  uint8_t* p;
  explicit Buf(size_t n) : v(n + 128 + QMAT_TAIL_SLACK, 0) {
    p = reinterpret_cast<uint8_t*>((reinterpret_cast<uintptr_t>(v.data()) + 63) & ~uintptr_t(63));
  }
};

// value patterns: 0 random, 1 extreme (+-max), 2 all +max, 3 all -max, 4 alternating +-max
static inline int pick_w(int pat, int wmax) {
  switch (pat) {
    case 1: return (rnd64() & 1) ? wmax : -wmax;
    case 2: return wmax;
    case 3: return -wmax;
    case 4: return (rnd64() & 2) ? wmax : -wmax;
    default: return rndi(-wmax, wmax);
  }
}
static inline int pick_a(int pat, bool biased) {  // signed value qa (biased) or raw [0,127]
  if (biased) {
    switch (pat) {
      case 1: return (rnd64() & 1) ? 127 : -128;
      case 2: return 127;
      case 3: return -128;
      case 4: return (rnd64() & 2) ? 127 : -128;
      default: return rndi(-128, 127);
    }
  }
  switch (pat) {
    case 1: return (rnd64() & 1) ? 127 : 0;
    case 2: case 3: return 127;
    case 4: return (rnd64() & 2) ? 127 : 0;
    default: return rndi(0, 127);
  }
}
static inline int pattern_of(int cs) { return cs % 29 == 0 ? 1 : cs % 29 == 1 ? 2 : cs % 29 == 2 ? 3 : cs % 29 == 3 ? 4 : 0; }

static void ref_dots(const int8_t* qw, int d_out, int d_in, const int* qa, int32_t* dot) {
  for (int o = 0; o < d_out; o++) {
    int64_t s = 0;
    for (int i = 0; i < d_in; i++) s += static_cast<int64_t>(qa[i]) * qw[static_cast<size_t>(o) * d_in + i];
    dot[o] = static_cast<int32_t>(s);
  }
}

// ---------------------------------------------------------------------------
static void test_dense(int d_out, int d_in, bool biased, int cases) {
  const int rows_pad = qmat_round_up(d_out, qmat_group_rows(d_in));
  std::vector<int8_t> qw(static_cast<size_t>(d_out) * d_in);
  std::vector<float> fold(d_out);
  std::vector<int> qa(d_in);
  alignas(64) static uint8_t act[768];
  std::vector<int32_t> dref(rows_pad), d2(rows_pad), d5(rows_pad);
  std::vector<float> f2(rows_pad), f5(rows_pad), r2(rows_pad), r5(rows_pad), res(rows_pad);
  Buf arena(qdense_bytes(d_out, d_in));
  const bool epi_c = (d_in == 192 && rows_pad <= 768);
  Buf q2b(rows_pad + 64), q5b(rows_pad + 64);  // 64B-aligned like the model's buffers (phase 2 uses aligned loads)
  uint8_t* q2 = q2b.p;
  uint8_t* q5 = q5b.p;
  std::vector<uint16_t> i2(rows_pad + 16), i5(rows_pad + 16);
  int first;
  for (int cs = 0; cs < cases; cs++) {
    const int pat = pattern_of(cs);
    for (size_t i = 0; i < qw.size(); i++) qw[i] = static_cast<int8_t>(pick_w(pat, QMAT_WMAX));
    for (int o = 0; o < d_out; o++) fold[o] = rnd_scale();
    std::memset(act, 0, sizeof(act));
    for (int i = 0; i < d_in; i++) {
      qa[i] = pick_a(pat, biased);
      act[i] = static_cast<uint8_t>(biased ? qa[i] + 128 : qa[i]);
    }
    QDense m = qdense_build(arena.p, qw.data(), fold.data(), d_out, d_in, biased);
    ref_dots(qw.data(), d_out, d_in, qa.data(), dref.data());
    for (int o = d_out; o < rows_pad; o++) dref[o] = 0;
    qgemv_i32(m, act, d2.data());
    avx512::qgemv_i32(m, act, d5.data());
    for (int o = 0; o < rows_pad; o++) {
      CHECK(d5[o] == dref[o], "i32 %dx%d cs %d row %d: avx512 %d ref %d", d_out, d_in, cs, o, d5[o], dref[o]);
      CHECK(d5[o] == d2[o], "i32 %dx%d cs %d row %d: avx512 %d avx2 %d", d_out, d_in, cs, o, d5[o], d2[o]);
    }
    // (a)
    qgemv_f32(m, act, f2.data());
    avx512::qgemv_f32(m, act, f5.data());
    CHECK(bits_eq(f2.data(), f5.data(), rows_pad, &first), "f32 %dx%d cs %d row %d: %a vs %a", d_out, d_in, cs, first,
          f2[first], f5[first]);
    avx512::qgemv_f32_nopf(m, act, f5.data());
    CHECK(bits_eq(f2.data(), f5.data(), rows_pad, &first), "f32_nopf %dx%d cs %d row %d", d_out, d_in, cs, first);
    // (b) residual add
    for (int o = 0; o < rows_pad; o++) res[o] = (rndf01() - 0.5f) * std::exp2f(-10.0f + 20.0f * rndf01());
    r2 = res; r5 = res;
    qgemv_add(m, act, r2.data());
    avx512::qgemv_add(m, act, r5.data());
    CHECK(bits_eq(r2.data(), r5.data(), rows_pad, &first), "add %dx%d cs %d row %d: %a vs %a", d_out, d_in, cs, first,
          r2[first], r5[first]);
    // (e)/(f) dynamic-scale variants
    const float s = rnd_pos_scale();
    qgemv_f32s(m, act, s, f2.data());
    avx512::qgemv_f32s(m, act, s, f5.data());
    CHECK(bits_eq(f2.data(), f5.data(), rows_pad, &first), "f32s %dx%d cs %d row %d", d_out, d_in, cs, first);
    r2 = res; r5 = res;
    qgemv_adds(m, act, s, r2.data());
    avx512::qgemv_adds(m, act, s, r5.data());
    CHECK(bits_eq(r2.data(), r5.data(), rows_pad, &first), "adds %dx%d cs %d row %d", d_out, d_in, cs, first);
    if (epi_c) {
      // (c) relu2q
      const float s_next = rnd_pos_scale() * 1e-3f;
      std::memset(q2, 0xAB, rows_pad + 64);
      std::memset(q5, 0xAB, rows_pad + 64);
      const int n2 = qgemv_relu2q(m, act, s_next, q2, i2.data());
      const int n5 = avx512::qgemv_relu2q(m, act, s_next, q5, i5.data());
      CHECK(n2 == n5, "relu2q nnz %dx%d cs %d: %d vs %d", d_out, d_in, cs, n2, n5);
      CHECK(std::memcmp(q2, q5, rows_pad) == 0, "relu2q q_out %dx%d cs %d", d_out, d_in, cs);
      if (n2 == n5) CHECK(std::memcmp(i2.data(), i5.data(), sizeof(uint16_t) * n2) == 0, "relu2q idx %dx%d cs %d", d_out, d_in, cs);
      // (g) relu2q_dyn
      float sn2 = -1, sn5 = -2;
      const int m2 = qgemv_relu2q_dyn(m, act, s, q2, i2.data(), &sn2);
      const int m5 = avx512::qgemv_relu2q_dyn(m, act, s, q5, i5.data(), &sn5);
      CHECK(m2 == m5 && bit_eq(sn2, sn5), "relu2q_dyn %dx%d cs %d: nnz %d/%d s %a/%a", d_out, d_in, cs, m2, m5, sn2, sn5);
      CHECK(std::memcmp(q2, q5, rows_pad) == 0, "relu2q_dyn q_out %dx%d cs %d", d_out, d_in, cs);
      if (m2 == m5) CHECK(std::memcmp(i2.data(), i5.data(), sizeof(uint16_t) * m2) == 0, "relu2q_dyn idx %dx%d cs %d", d_out, d_in, cs);
      // (d) quant_bias, (h) quant_bias_dyn
      qgemv_quant_bias(m, act, s_next, q2);
      avx512::qgemv_quant_bias(m, act, s_next, q5);
      CHECK(std::memcmp(q2, q5, rows_pad) == 0, "quant_bias %dx%d cs %d", d_out, d_in, cs);
      const float y2 = qgemv_quant_bias_dyn(m, act, s, q2);
      const float y5 = avx512::qgemv_quant_bias_dyn(m, act, s, q5);
      CHECK(bit_eq(y2, y5) && std::memcmp(q2, q5, rows_pad) == 0, "quant_bias_dyn %dx%d cs %d: %a/%a",
            d_out, d_in, cs, y2, y5);
    }
  }
  std::printf("dense %3dx%3d %s: %d cases OK\n", d_out, d_in, biased ? "biased" : "raw", cases);
}

// packed int4 + LUT arena (AVX-512 only) vs the AVX2 dense kernels on the same logical weights
static void test_pcb(int d_out, int d_in, bool biased, int cases) {
  const int rows_pad8 = qmat_round_up(d_out, 8);
  const int rows_pad = qmat_round_up(d_out, qmat_group_rows(d_in));  // dense arena padding (4 for 768-in)
  const int rows_cmp = std::min(rows_pad, rows_pad8);
  std::vector<int8_t> q(static_cast<size_t>(d_out) * d_in), wv(q.size());
  std::vector<float> fold(d_out);
  std::vector<int> qa(d_in);
  alignas(64) static uint8_t act[768];
  std::vector<int32_t> dref(rows_pad8), d2(rows_pad), d5(rows_pad8);
  std::vector<float> f2(rows_pad), f5(rows_pad8), r2(rows_pad), r5(rows_pad8), res(rows_pad8);
  Buf dense(qdense_bytes(d_out, d_in)), pcb(qpackedcb_bytes(d_out, d_in));
  Buf q2b(rows_pad8 + 64), q5b(rows_pad8 + 64);
  std::vector<uint16_t> i2(rows_pad8 + 16), i5(rows_pad8 + 16);
  const bool epi_c = (d_in == 192 && rows_pad8 <= 768);
  int first;
  for (int cs = 0; cs < cases; cs++) {
    const int pat = pattern_of(cs);
    int8_t cb[15];
    for (int k = 0; k < 15; k++) cb[k] = static_cast<int8_t>(k - 7);
#if QMAT_CODEBOOK
    // random signed codebook, |v| <= QMAT_WMAX (any level may be nonzero: pads use LUT entry 15); extreme cases +-WMAX
    for (int k = 0; k < 15; k++)
      cb[k] = static_cast<int8_t>(pat == 0 ? rndi(-QMAT_WMAX, QMAT_WMAX) : ((k & 1) ? QMAT_WMAX : -QMAT_WMAX));
#endif
    for (size_t i = 0; i < q.size(); i++) {
      q[i] = static_cast<int8_t>(pick_w(pat, 7));
      wv[i] = cb[q[i] + 7];
    }
    for (int o = 0; o < d_out; o++) fold[o] = rnd_scale();
    std::memset(act, 0, sizeof(act));
    for (int i = 0; i < d_in; i++) {
      qa[i] = pick_a(pat, biased);
      act[i] = static_cast<uint8_t>(biased ? qa[i] + 128 : qa[i]);
    }
    QDense md = qdense_build(dense.p, wv.data(), fold.data(), d_out, d_in, biased);
    QPackedCB mp = qpackedcb_build(pcb.p, q.data(), QMAT_CODEBOOK ? cb : nullptr, fold.data(), d_out, d_in, biased);
    ref_dots(wv.data(), d_out, d_in, qa.data(), dref.data());
    for (int o = d_out; o < rows_pad8; o++) dref[o] = 0;
    qgemv_i32(md, act, d2.data());
    avx512::qgemv_pcb_i32(mp, act, d5.data());
    for (int o = 0; o < rows_pad8; o++) CHECK(d5[o] == dref[o], "pcb i32 %dx%d cs %d row %d: %d ref %d", d_out, d_in, cs, o, d5[o], dref[o]);
    for (int o = 0; o < rows_cmp; o++) CHECK(d5[o] == d2[o], "pcb i32 vs avx2 %dx%d cs %d row %d", d_out, d_in, cs, o);
    qgemv_f32(md, act, f2.data());
    avx512::qgemv_pcb_f32(mp, act, f5.data());
    CHECK(bits_eq(f2.data(), f5.data(), rows_cmp, &first), "pcb f32 %dx%d cs %d row %d: %a vs %a", d_out, d_in, cs, first, f2[first], f5[first]);
    for (int o = 0; o < rows_pad8; o++) res[o] = (rndf01() - 0.5f) * std::exp2f(-10.0f + 20.0f * rndf01());
    r2.assign(res.begin(), res.begin() + rows_pad); r5 = res;
    qgemv_add(md, act, r2.data());
    avx512::qgemv_pcb_add(mp, act, r5.data());
    CHECK(bits_eq(r2.data(), r5.data(), rows_cmp, &first), "pcb add %dx%d cs %d row %d", d_out, d_in, cs, first);
    const float s = rnd_pos_scale();
    qgemv_f32s(md, act, s, f2.data());
    avx512::qgemv_pcb_f32s(mp, act, s, f5.data());
    CHECK(bits_eq(f2.data(), f5.data(), rows_cmp, &first), "pcb f32s %dx%d cs %d row %d", d_out, d_in, cs, first);
    r2.assign(res.begin(), res.begin() + rows_pad); r5 = res;
    qgemv_adds(md, act, s, r2.data());
    avx512::qgemv_pcb_adds(mp, act, s, r5.data());
    CHECK(bits_eq(r2.data(), r5.data(), rows_cmp, &first), "pcb adds %dx%d cs %d row %d", d_out, d_in, cs, first);
    if (epi_c) {
      const float s_next = rnd_pos_scale() * 1e-3f;
      const int n2 = qgemv_relu2q(md, act, s_next, q2b.p, i2.data());
      const int n5 = avx512::qgemv_pcb_relu2q(mp, act, s_next, q5b.p, i5.data());
      CHECK(n2 == n5 && std::memcmp(q2b.p, q5b.p, rows_pad8) == 0 && std::memcmp(i2.data(), i5.data(), 2 * n2) == 0,
            "pcb relu2q %dx%d cs %d (nnz %d/%d)", d_out, d_in, cs, n2, n5);
      float sn2 = -1, sn5 = -2;
      const int m2 = qgemv_relu2q_dyn(md, act, s, q2b.p, i2.data(), &sn2);
      const int m5 = avx512::qgemv_pcb_relu2q_dyn(mp, act, s, q5b.p, i5.data(), &sn5);
      CHECK(m2 == m5 && bit_eq(sn2, sn5) && std::memcmp(q2b.p, q5b.p, rows_pad8) == 0 && std::memcmp(i2.data(), i5.data(), 2 * m2) == 0,
            "pcb relu2q_dyn %dx%d cs %d", d_out, d_in, cs);
      qgemv_quant_bias(md, act, s_next, q2b.p);
      avx512::qgemv_pcb_quant_bias(mp, act, s_next, q5b.p);
      CHECK(std::memcmp(q2b.p, q5b.p, rows_pad8) == 0, "pcb quant_bias %dx%d cs %d", d_out, d_in, cs);
      const float y2 = qgemv_quant_bias_dyn(md, act, s, q2b.p);
      const float y5 = avx512::qgemv_pcb_quant_bias_dyn(mp, act, s, q5b.p);
      CHECK(bit_eq(y2, y5) && std::memcmp(q2b.p, q5b.p, rows_pad8) == 0, "pcb quant_bias_dyn %dx%d cs %d", d_out, d_in, cs);
    }
  }
  std::printf("pcb   %3dx%3d %s: %d cases OK (vs AVX2 dense + scalar ref)\n", d_out, d_in, biased ? "biased" : "raw", cases);
}

// ---------------------------------------------------------------------------
static void test_qw8(int d_out, int d_in, bool biased, int cases) {
  const int rows_pad = qmat_round_up(d_out, 8), stride = qmat_round_up(d_in, 32);
  std::vector<int8_t> qw(static_cast<size_t>(d_out) * d_in);
  std::vector<float> fold(d_out);
  std::vector<int> qa(d_in);
  alignas(64) static uint8_t act[256];
  std::vector<int32_t> dref(rows_pad);
  std::vector<float> f2(rows_pad), f5(rows_pad);
  Buf wb(qw8_bytes(d_out, d_in));
  alignas(64) static int32_t corr[256];
  alignas(64) static float fld[256];
  int first;
  for (int cs = 0; cs < cases; cs++) {
    const int pat = pattern_of(cs);
    for (size_t i = 0; i < qw.size(); i++) qw[i] = static_cast<int8_t>(pick_w(pat, 127));
    for (int o = 0; o < d_out; o++) fold[o] = rnd_scale();
    std::memset(act, 0, sizeof(act));
    for (int i = 0; i < d_in; i++) {
      qa[i] = pick_a(pat, biased);
      act[i] = static_cast<uint8_t>(biased ? qa[i] + 128 : qa[i]);
    }
    QW8 m = qw8_build(reinterpret_cast<int8_t*>(wb.p), corr, fld, qw.data(), fold.data(), d_out, d_in, biased);
    (void)stride;
    ref_dots(qw.data(), d_out, d_in, qa.data(), dref.data());
    qw8_f32(m, act, f2.data());
    avx512::qw8_f32(m, act, f5.data());
    CHECK(bits_eq(f2.data(), f5.data(), rows_pad, &first), "qw8 %dx%d cs %d row %d: %a vs %a", d_out, d_in, cs, first,
          f2[first], f5[first]);
    for (int o = 0; o < rows_pad; o++) {
      const float want = o < d_out ? fold[o] * static_cast<float>(dref[o]) : 0.0f;
      CHECK(bit_eq(f5[o], want), "qw8 ref %dx%d cs %d row %d: %a want %a", d_out, d_in, cs, o, f5[o], want);
    }
  }
  std::printf("qw8   %3dx%3d %s: %d cases OK\n", d_out, d_in, biased ? "biased" : "raw", cases);
}

// ---------------------------------------------------------------------------
static void test_sparse4(int d_in, int cases) {
  std::vector<int8_t> qw(static_cast<size_t>(192) * d_in);
  std::vector<float> fold(192);
  std::vector<int> qa(d_in);
  std::vector<uint8_t> q8(qmat_round_up(d_in, 32) + 64, 0);
  std::vector<uint16_t> idx(d_in + 16);
  std::vector<int32_t> dref(192), d2(192), d5(192);
  std::vector<float> f2(192), f5(192), res(192), r2(192), r5(192);
  Buf cols(qsparse4_bytes(d_in));
  alignas(64) static float fold4[192];
  int first;
  for (int cs = 0; cs < cases; cs++) {
    const int pat = pattern_of(cs);
    // sparse4 arena holds level indices [-7,7]; codebook build maps them through the LUT (|v| <= QMAT_WMAX)
    for (size_t i = 0; i < qw.size(); i++) qw[i] = static_cast<int8_t>(pick_w(pat, 7));
    for (int o = 0; o < 192; o++) fold[o] = rnd_scale();
    const float dens = cs % 5 == 0 ? 1.0f : cs % 5 == 1 ? 0.05f : rndf01();
    std::fill(q8.begin(), q8.end(), 0);
    int nnz = 0;
    for (int i = 0; i < d_in; i++) {
      const bool nz = rndf01() < dens;
      int v = nz ? (pat == 0 ? rndi(1, 127) : 127) : 0;
      qa[i] = v;
      q8[i] = static_cast<uint8_t>(v);
      if (v) idx[nnz++] = static_cast<uint16_t>(i);
    }
    for (int k = nnz; k < nnz + 8; k++) idx[k] = nnz ? idx[nnz - 1] : 0;
    QSparse4 m = qsparse4_build(cols.p, fold4, qw.data(), fold.data(), 192, d_in);
#if QMAT_CODEBOOK
    // random signed codebook with |v| <= QMAT_WMAX (entry 15 = 0), the arena's LUT (both 16-byte lanes)
    int8_t cb[16];
    for (int k = 0; k < 15; k++) cb[k] = static_cast<int8_t>(pat == 0 ? rndi(-QMAT_WMAX, QMAT_WMAX) : ((k & 1) ? QMAT_WMAX : -QMAT_WMAX));
    cb[15] = 0;
    std::memcpy(m.lut, cb, 16);
    std::memcpy(m.lut + 16, cb, 16);
    std::vector<int8_t> wv(qw.size());
    for (size_t i = 0; i < qw.size(); i++) wv[i] = cb[qw[i] + 7];
    ref_dots(wv.data(), 192, d_in, qa.data(), dref.data());
#else
    ref_dots(qw.data(), 192, d_in, qa.data(), dref.data());
#endif
    qsparse4_i32(m, q8.data(), idx.data(), nnz, d2.data());
    avx512::qsparse4_i32(m, q8.data(), idx.data(), nnz, d5.data());
    for (int o = 0; o < 192; o++) {
      CHECK(d5[o] == dref[o], "sparse4 i32 d_in %d cs %d nnz %d row %d: %d ref %d", d_in, cs, nnz, o, d5[o], dref[o]);
      CHECK(d5[o] == d2[o], "sparse4 i32 d_in %d cs %d row %d: %d avx2 %d", d_in, cs, o, d5[o], d2[o]);
    }
    avx512::qsparse4_dense_i32(m, q8.data(), d5.data());
    for (int o = 0; o < 192; o++) CHECK(d5[o] == dref[o], "sparse4 dense i32 d_in %d cs %d row %d", d_in, cs, o);
    qsparse4_f32(m, q8.data(), idx.data(), nnz, f2.data());
    avx512::qsparse4_f32(m, q8.data(), idx.data(), nnz, f5.data());
    CHECK(bits_eq(f2.data(), f5.data(), 192, &first), "sparse4 f32 d_in %d cs %d row %d: %a vs %a", d_in, cs, first, f2[first], f5[first]);
    avx512::qsparse4_dense_f32(m, q8.data(), f5.data());
    CHECK(bits_eq(f2.data(), f5.data(), 192, &first), "sparse4 dense f32 d_in %d cs %d row %d", d_in, cs, first);
    for (int o = 0; o < 192; o++) res[o] = (rndf01() - 0.5f) * std::exp2f(-10.0f + 20.0f * rndf01());
    r2 = res; r5 = res;
    qsparse4_add(m, q8.data(), idx.data(), nnz, r2.data());
    avx512::qsparse4_add(m, q8.data(), idx.data(), nnz, r5.data());
    CHECK(bits_eq(r2.data(), r5.data(), 192, &first), "sparse4 add d_in %d cs %d row %d", d_in, cs, first);
    r5 = res;
    avx512::qsparse4_dense_add(m, q8.data(), r5.data());
    CHECK(bits_eq(r2.data(), r5.data(), 192, &first), "sparse4 dense add d_in %d cs %d row %d", d_in, cs, first);
    const float s = rnd_pos_scale();
    qsparse4_f32s(m, q8.data(), idx.data(), nnz, s, f2.data());
    avx512::qsparse4_f32s(m, q8.data(), idx.data(), nnz, s, f5.data());
    CHECK(bits_eq(f2.data(), f5.data(), 192, &first), "sparse4 f32s d_in %d cs %d row %d", d_in, cs, first);
    avx512::qsparse4_dense_f32s(m, q8.data(), s, f5.data());
    CHECK(bits_eq(f2.data(), f5.data(), 192, &first), "sparse4 dense f32s d_in %d cs %d row %d", d_in, cs, first);
    r2 = res; r5 = res;
    qsparse4_adds(m, q8.data(), idx.data(), nnz, s, r2.data());
    avx512::qsparse4_adds(m, q8.data(), idx.data(), nnz, s, r5.data());
    CHECK(bits_eq(r2.data(), r5.data(), 192, &first), "sparse4 adds d_in %d cs %d row %d", d_in, cs, first);
    r5 = res;
    avx512::qsparse4_dense_adds(m, q8.data(), s, r5.data());
    CHECK(bits_eq(r2.data(), r5.data(), 192, &first), "sparse4 dense adds d_in %d cs %d row %d", d_in, cs, first);
  }
  std::printf("sparse4 192x%3d: %d cases OK\n", d_in, cases);
}

int main(int argc, char** argv) {
  setvbuf(stdout, nullptr, _IOLBF, 0);
  const int N = argc > 1 ? std::atoi(argv[1]) : 3000;
  if (!cpu_has_avx512_vnni()) {
    std::printf("SKIP: this CPU has no AVX-512 VNNI (or FX2_FORCE_AVX2=1 / TF_AVX512=0 build)\n");
    return 2;
  }
  std::printf("QMAT_CODEBOOK=%d QMAT_WMAX=%d QMAT_SMALL_W8=%d, %d cases per shape\n", QMAT_CODEBOOK, QMAT_WMAX, QMAT_SMALL_W8, N);
  test_dense(192, 192, true, N);
  test_dense(768, 192, true, N);
  test_dense(64, 192, true, N);
  test_dense(192, 64, true, N);
  test_dense(205, 192, true, N);
  test_dense(192, 205, false, N);
  test_dense(192, 768, false, N);
  test_dense(192, 768, true, N);
  test_dense(196, 768, true, N / 4);  // odd number of 4-row groups (tail path)
  test_dense(200, 192, false, N / 4);  // 25 groups, raw
  test_pcb(192, 192, true, N);
  test_pcb(768, 192, true, N);
  test_pcb(64, 192, true, N);
  test_pcb(192, 64, true, N);
  test_pcb(205, 192, true, N);
  test_pcb(192, 205, false, N / 2);
  test_pcb(192, 768, false, N / 2);
  test_pcb(192, 768, true, N / 2);
  test_qw8(192, 205, false, N);
  test_qw8(205, 192, true, N);
  test_qw8(64, 192, true, N / 4);
  test_sparse4(768, N);
  test_sparse4(205, N);
  if (g_fail == 0) {
    std::printf("ALL AVX2-vs-AVX512 EQUALITY CHECKS PASSED (%ld checks)\n", g_checks);
    return 0;
  }
  std::printf("FAILURES: %ld (of %ld checks)\n", g_fail, g_checks);
  return 1;
}
