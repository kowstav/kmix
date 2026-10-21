// qmat_sparse_avx512.cpp -- AVX-512 VNNI variant of the int4 column (QSparse4)
// kernels (TF_AVX512 fast path, 2026-09-19). Same arena (shared with the AVX2
// path), same contracts as qmat_sparse.h, bit-identical results. Compiled with
// -mavx512f -mavx512bw -mavx512vl -mavx512vnni on top of the x86-64-v3 baseline;
// only reachable behind cpu_has_avx512_vnni() (qmat_cpu.h).
//
// Four columns per step: the 96 nibble bytes of each column are unpacked
// (low nibbles = rows 0..95, high = rows 96..191; codebook build: mapped
// through the per-matrix LUT with vpshufb), the four columns are interleaved
// bytewise into dwords [c0 c1 c2 c3] per row (vpunpck bw/wd, per 128-bit
// lane) and vpdpbusd accumulates the 4 products of every row straight into
// int32 lanes: 16 accumulators (12 zmm-equivalents) hold all 192 rows for the
// whole matmul — no int16 stage, no periodic flush. The lane->row permutation
// introduced by the in-lane unpacks is undone once at the end (128-bit lane
// transposes) when the accumulators are written to acc[192].
//   plain build:    nibbles (w+7, u8 operand) x acts (s8 operand, <= 127); the
//                   global correction 7*sum(acts) is subtracted in int32.
//   codebook build: LUT'd signed weights (s8 operand) x acts (u8 operand).
#include "qmat_avx512.h"

#include <immintrin.h>

#include <algorithm>
#include <cstring>

namespace fx2 {
namespace opt {
namespace avx512 {

namespace {

constexpr int PF_QUADS_AHEAD = 2;  // = 8 columns ahead, like the AVX2 kernel's 4 pairs

struct Acc {
  __m512i A[4];  // rows   0.. 63: A[k] lane 4L+j <-> row 16L + 4k + j
  __m512i B[4];  // rows  96..159: B[k] lane 4L+j <-> row 96 + 16L + 4k + j
  __m256i C[4];  // rows  64.. 95: C[k] lane 4L+j <-> row 64 + 16L + 4k + j (L = 0,1)
  __m256i D[4];  // rows 160..191
};

inline void acc_zero(Acc& a) {
  for (int k = 0; k < 4; k++) {
    a.A[k] = _mm512_setzero_si512();
    a.B[k] = _mm512_setzero_si512();
    a.C[k] = _mm256_setzero_si256();
    a.D[k] = _mm256_setzero_si256();
  }
}

// 4 x 64 B column parts (already nibble-unpacked / LUT'd) -> 4 dword-interleaved zmm
inline void ilv512(__m512i c0, __m512i c1, __m512i c2, __m512i c3, __m512i q[4]) {
  const __m512i t01l = _mm512_unpacklo_epi8(c0, c1);
  const __m512i t01h = _mm512_unpackhi_epi8(c0, c1);
  const __m512i t23l = _mm512_unpacklo_epi8(c2, c3);
  const __m512i t23h = _mm512_unpackhi_epi8(c2, c3);
  q[0] = _mm512_unpacklo_epi16(t01l, t23l);
  q[1] = _mm512_unpackhi_epi16(t01l, t23l);
  q[2] = _mm512_unpacklo_epi16(t01h, t23h);
  q[3] = _mm512_unpackhi_epi16(t01h, t23h);
}
inline void ilv256(__m256i c0, __m256i c1, __m256i c2, __m256i c3, __m256i q[4]) {
  const __m256i t01l = _mm256_unpacklo_epi8(c0, c1);
  const __m256i t01h = _mm256_unpackhi_epi8(c0, c1);
  const __m256i t23l = _mm256_unpacklo_epi8(c2, c3);
  const __m256i t23h = _mm256_unpackhi_epi8(c2, c3);
  q[0] = _mm256_unpacklo_epi16(t01l, t23l);
  q[1] = _mm256_unpackhi_epi16(t01l, t23l);
  q[2] = _mm256_unpacklo_epi16(t01h, t23h);
  q[3] = _mm256_unpackhi_epi16(t01h, t23h);
}

#if QMAT_CODEBOOK
// signed LUT'd weights are the s8 operand, the act dword the u8 operand
#define QS512_DP(acc, w, a) _mm512_dpbusd_epi32((acc), (a), (w))
#define QS256_DP(acc, w, a) _mm256_dpbusd_epi32((acc), (a), (w))
#else
// unsigned nibbles are the u8 operand, the act dword (values <= 127) the s8 operand
#define QS512_DP(acc, w, a) _mm512_dpbusd_epi32((acc), (w), (a))
#define QS256_DP(acc, w, a) _mm256_dpbusd_epi32((acc), (w), (a))
#endif

struct Ctx {
  __m512i m0F;
  __m512i lut;  // codebook: 16-byte table in all four lanes
};

// one quad of columns (pointers) with the act dword a4 (bytes v0..v3)
inline void quad(const Ctx& cx, Acc& acc, const uint8_t* p0, const uint8_t* p1, const uint8_t* p2, const uint8_t* p3,
                 __m512i a4) {
  const __m256i a4y = _mm512_castsi512_si256(a4);
  const __m256i m0Fy = _mm512_castsi512_si256(cx.m0F);
  __m512i q[4];
  // ---- rows 0..63 (low nibbles of bytes 0..63) ----
  {
    const __m512i w0 = _mm512_load_si512(p0), w1 = _mm512_load_si512(p1);
    const __m512i w2 = _mm512_load_si512(p2), w3 = _mm512_load_si512(p3);
    __m512i c0 = _mm512_and_si512(w0, cx.m0F), c1 = _mm512_and_si512(w1, cx.m0F);
    __m512i c2 = _mm512_and_si512(w2, cx.m0F), c3 = _mm512_and_si512(w3, cx.m0F);
#if QMAT_CODEBOOK
    c0 = _mm512_shuffle_epi8(cx.lut, c0); c1 = _mm512_shuffle_epi8(cx.lut, c1);
    c2 = _mm512_shuffle_epi8(cx.lut, c2); c3 = _mm512_shuffle_epi8(cx.lut, c3);
#endif
    ilv512(c0, c1, c2, c3, q);
    for (int k = 0; k < 4; k++) acc.A[k] = QS512_DP(acc.A[k], q[k], a4);
    // ---- rows 96..159 (high nibbles of bytes 0..63) ----
    c0 = _mm512_and_si512(_mm512_srli_epi16(w0, 4), cx.m0F); c1 = _mm512_and_si512(_mm512_srli_epi16(w1, 4), cx.m0F);
    c2 = _mm512_and_si512(_mm512_srli_epi16(w2, 4), cx.m0F); c3 = _mm512_and_si512(_mm512_srli_epi16(w3, 4), cx.m0F);
#if QMAT_CODEBOOK
    c0 = _mm512_shuffle_epi8(cx.lut, c0); c1 = _mm512_shuffle_epi8(cx.lut, c1);
    c2 = _mm512_shuffle_epi8(cx.lut, c2); c3 = _mm512_shuffle_epi8(cx.lut, c3);
#endif
    ilv512(c0, c1, c2, c3, q);
    for (int k = 0; k < 4; k++) acc.B[k] = QS512_DP(acc.B[k], q[k], a4);
  }
  // ---- rows 64..95 / 160..191 (bytes 64..95) ----
  {
    const __m256i luty = _mm512_castsi512_si256(cx.lut);
    (void)luty;
    const __m256i x0 = _mm256_load_si256(reinterpret_cast<const __m256i*>(p0 + 64));
    const __m256i x1 = _mm256_load_si256(reinterpret_cast<const __m256i*>(p1 + 64));
    const __m256i x2 = _mm256_load_si256(reinterpret_cast<const __m256i*>(p2 + 64));
    const __m256i x3 = _mm256_load_si256(reinterpret_cast<const __m256i*>(p3 + 64));
    __m256i c0 = _mm256_and_si256(x0, m0Fy), c1 = _mm256_and_si256(x1, m0Fy);
    __m256i c2 = _mm256_and_si256(x2, m0Fy), c3 = _mm256_and_si256(x3, m0Fy);
#if QMAT_CODEBOOK
    c0 = _mm256_shuffle_epi8(luty, c0); c1 = _mm256_shuffle_epi8(luty, c1);
    c2 = _mm256_shuffle_epi8(luty, c2); c3 = _mm256_shuffle_epi8(luty, c3);
#endif
    __m256i qy[4];
    ilv256(c0, c1, c2, c3, qy);
    for (int k = 0; k < 4; k++) acc.C[k] = QS256_DP(acc.C[k], qy[k], a4y);
    c0 = _mm256_and_si256(_mm256_srli_epi16(x0, 4), m0Fy); c1 = _mm256_and_si256(_mm256_srli_epi16(x1, 4), m0Fy);
    c2 = _mm256_and_si256(_mm256_srli_epi16(x2, 4), m0Fy); c3 = _mm256_and_si256(_mm256_srli_epi16(x3, 4), m0Fy);
#if QMAT_CODEBOOK
    c0 = _mm256_shuffle_epi8(luty, c0); c1 = _mm256_shuffle_epi8(luty, c1);
    c2 = _mm256_shuffle_epi8(luty, c2); c3 = _mm256_shuffle_epi8(luty, c3);
#endif
    ilv256(c0, c1, c2, c3, qy);
    for (int k = 0; k < 4; k++) acc.D[k] = QS256_DP(acc.D[k], qy[k], a4y);
  }
}

// write the accumulators to acc[192] in natural row order
inline void acc_store(const Acc& a, int32_t* out) {
  // zmm groups: rows base + 16L + 4k + j = X[k] lane 4L+j  ->  out zmm L = [X0.L, X1.L, X2.L, X3.L] (128-bit lanes)
  auto tr = [](const __m512i X[4], int32_t* o) {
    const __m512i u0 = _mm512_shuffle_i32x4(X[0], X[1], _MM_SHUFFLE(1, 0, 1, 0));  // [X0.L0 X0.L1 X1.L0 X1.L1]
    const __m512i u1 = _mm512_shuffle_i32x4(X[2], X[3], _MM_SHUFFLE(1, 0, 1, 0));  // [X2.L0 X2.L1 X3.L0 X3.L1]
    const __m512i u2 = _mm512_shuffle_i32x4(X[0], X[1], _MM_SHUFFLE(3, 2, 3, 2));  // [X0.L2 X0.L3 X1.L2 X1.L3]
    const __m512i u3 = _mm512_shuffle_i32x4(X[2], X[3], _MM_SHUFFLE(3, 2, 3, 2));
    _mm512_store_si512(o + 0, _mm512_shuffle_i32x4(u0, u1, _MM_SHUFFLE(2, 0, 2, 0)));   // [X0.L0 X1.L0 X2.L0 X3.L0]
    _mm512_store_si512(o + 16, _mm512_shuffle_i32x4(u0, u1, _MM_SHUFFLE(3, 1, 3, 1)));  // L1
    _mm512_store_si512(o + 32, _mm512_shuffle_i32x4(u2, u3, _MM_SHUFFLE(2, 0, 2, 0)));  // L2
    _mm512_store_si512(o + 48, _mm512_shuffle_i32x4(u2, u3, _MM_SHUFFLE(3, 1, 3, 1)));  // L3
  };
  auto tr256 = [](const __m256i X[4], int32_t* o) {
    _mm256_store_si256(reinterpret_cast<__m256i*>(o + 0), _mm256_permute2x128_si256(X[0], X[1], 0x20));
    _mm256_store_si256(reinterpret_cast<__m256i*>(o + 8), _mm256_permute2x128_si256(X[2], X[3], 0x20));
    _mm256_store_si256(reinterpret_cast<__m256i*>(o + 16), _mm256_permute2x128_si256(X[0], X[1], 0x31));
    _mm256_store_si256(reinterpret_cast<__m256i*>(o + 24), _mm256_permute2x128_si256(X[2], X[3], 0x31));
  };
  tr(a.A, out);
  tr256(a.C, out + 64);
  tr(a.B, out + 96);
  tr256(a.D, out + 160);
}

inline Ctx make_ctx(const QSparse4& m) {
  Ctx cx;
  cx.m0F = _mm512_set1_epi8(0x0F);
  cx.lut = _mm512_broadcast_i32x4(_mm_load_si128(reinterpret_cast<const __m128i*>(m.lut)));
  return cx;
}

inline __m512i act4(uint32_t v0, uint32_t v1, uint32_t v2, uint32_t v3) {
  return _mm512_set1_epi32(static_cast<int>(v0 | (v1 << 8) | (v2 << 16) | (v3 << 24)));
}

// returns the global int32 correction (plain build: 7 * sum(acts); codebook: 0)
template <bool PF>
int32_t sparse4_accum(const QSparse4& m, const uint8_t* __restrict q8, const uint16_t* __restrict idx, int nnz,
                      int32_t* __restrict acc_out) {
  const Ctx cx = make_ctx(m);
  const uint8_t* cols = m.cols;
  Acc acc;
  acc_zero(acc);
  uint32_t asum = 0;
  const int nq = nnz >> 2;
  for (int p = 0; p < nq; p++) {
    const uint16_t* ip = idx + 4 * p;
    if (PF) {
      const uint16_t* fp = ip + 4 * PF_QUADS_AHEAD;  // <= idx[nnz + 7]: inside the producers' slack
      for (int i = 0; i < 4; i++) {
        const char* f = reinterpret_cast<const char*>(cols) + 128u * fp[i];
        _mm_prefetch(f, _MM_HINT_T0);
        _mm_prefetch(f + 64, _MM_HINT_T0);
      }
    }
    const uint32_t i0 = ip[0], i1 = ip[1], i2 = ip[2], i3 = ip[3];
    const uint32_t v0 = q8[i0], v1 = q8[i1], v2 = q8[i2], v3 = q8[i3];
    asum += v0 + v1 + v2 + v3;
    quad(cx, acc, cols + 128u * i0, cols + 128u * i1, cols + 128u * i2, cols + 128u * i3, act4(v0, v1, v2, v3));
  }
  const int rem = nnz & 3;
  if (rem) {  // tail: missing slots repeat the last column with act 0 (contributes nothing)
    const uint16_t* ip = idx + 4 * nq;
    uint32_t ii[4], vv[4];
    for (int i = 0; i < 4; i++) {
      ii[i] = ip[i < rem ? i : rem - 1];
      vv[i] = i < rem ? q8[ii[i]] : 0u;
      asum += vv[i];
    }
    quad(cx, acc, cols + 128u * ii[0], cols + 128u * ii[1], cols + 128u * ii[2], cols + 128u * ii[3],
         act4(vv[0], vv[1], vv[2], vv[3]));
  }
  acc_store(acc, acc_out);
#if QMAT_CODEBOOK
  (void)asum;
  return 0;
#else
  return static_cast<int32_t>(7u * asum);
#endif
}

int32_t dense4_accum(const QSparse4& m, const uint8_t* __restrict q8, int32_t* __restrict acc_out) {
  const Ctx cx = make_ctx(m);
  const uint8_t* cols = m.cols;
  const int d_in = m.d_in;
  Acc acc;
  acc_zero(acc);
  uint32_t asum = 0;
  const int nq = d_in >> 2;
  for (int p = 0; p < nq; p++) {
    const char* f = reinterpret_cast<const char*>(cols) + 512u * p + 2048;
    for (int k = 0; k < 8; k++) _mm_prefetch(f + 64 * k, _MM_HINT_T0);
    const uint32_t c = 4u * p;
    const uint32_t v0 = q8[c], v1 = q8[c + 1], v2 = q8[c + 2], v3 = q8[c + 3];
    asum += v0 + v1 + v2 + v3;
    quad(cx, acc, cols + 128u * c, cols + 128u * (c + 1), cols + 128u * (c + 2), cols + 128u * (c + 3),
         act4(v0, v1, v2, v3));
  }
  const int rem = d_in & 3;
  if (rem) {
    uint32_t ii[4], vv[4];
    for (int i = 0; i < 4; i++) {
      ii[i] = 4u * nq + (i < rem ? i : rem - 1);
      vv[i] = i < rem ? q8[ii[i]] : 0u;
      asum += vv[i];
    }
    quad(cx, acc, cols + 128u * ii[0], cols + 128u * ii[1], cols + 128u * ii[2], cols + 128u * ii[3],
         act4(vv[0], vv[1], vv[2], vv[3]));
  }
  acc_store(acc, acc_out);
#if QMAT_CODEBOOK
  (void)asum;
  return 0;
#else
  return static_cast<int32_t>(7u * asum);
#endif
}

// ---- epilogues: verbatim op sequences of qmat_sparse.cpp epi4_* ----
inline void epi4_f32(const int32_t* acc, int32_t corr, const float* fold, float* out) {
  const __m256i vc = _mm256_set1_epi32(corr);
  for (int k = 0; k < 24; k++) {
    const __m256i d = _mm256_sub_epi32(_mm256_load_si256(reinterpret_cast<const __m256i*>(acc + 8 * k)), vc);
    const __m256 y = _mm256_mul_ps(_mm256_cvtepi32_ps(d), _mm256_load_ps(fold + 8 * k));
    _mm256_storeu_ps(out + 8 * k, y);
  }
}
inline void epi4_add(const int32_t* acc, int32_t corr, const float* fold, float* out) {
  const __m256i vc = _mm256_set1_epi32(corr);
  for (int k = 0; k < 24; k++) {
    const __m256i d = _mm256_sub_epi32(_mm256_load_si256(reinterpret_cast<const __m256i*>(acc + 8 * k)), vc);
    const __m256 y = _mm256_mul_ps(_mm256_cvtepi32_ps(d), _mm256_load_ps(fold + 8 * k));
    _mm256_storeu_ps(out + 8 * k, _mm256_add_ps(_mm256_loadu_ps(out + 8 * k), y));
  }
}
inline void epi4_f32s(const int32_t* acc, int32_t corr, const float* fold, float s, float* out) {
  const __m256i vc = _mm256_set1_epi32(corr);
  const __m256 vs = _mm256_set1_ps(s);
  for (int k = 0; k < 24; k++) {
    const __m256i d = _mm256_sub_epi32(_mm256_load_si256(reinterpret_cast<const __m256i*>(acc + 8 * k)), vc);
    const __m256 y = _mm256_mul_ps(_mm256_cvtepi32_ps(d), _mm256_load_ps(fold + 8 * k));
    _mm256_storeu_ps(out + 8 * k, _mm256_mul_ps(y, vs));
  }
}
inline void epi4_adds(const int32_t* acc, int32_t corr, const float* fold, float s, float* out) {
  const __m256i vc = _mm256_set1_epi32(corr);
  const __m256 vs = _mm256_set1_ps(s);
  for (int k = 0; k < 24; k++) {
    const __m256i d = _mm256_sub_epi32(_mm256_load_si256(reinterpret_cast<const __m256i*>(acc + 8 * k)), vc);
    __m256 y = _mm256_mul_ps(_mm256_cvtepi32_ps(d), _mm256_load_ps(fold + 8 * k));
    y = _mm256_mul_ps(y, vs);
    _mm256_storeu_ps(out + 8 * k, _mm256_add_ps(_mm256_loadu_ps(out + 8 * k), y));
  }
}

inline void warm_epilogue(const float* fold, const float* out) {
  for (int k = 0; k < 12; k++) _mm_prefetch(reinterpret_cast<const char*>(fold) + 64 * k, _MM_HINT_T0);
  if (out)
    for (int k = 0; k < 12; k++) _mm_prefetch(reinterpret_cast<const char*>(out) + 64 * k, _MM_HINT_T0);
}

}  // namespace

void qsparse4_f32(const QSparse4& m, const uint8_t* q8, const uint16_t* idx, int nnz, float* out) {
  alignas(64) int32_t acc[192];
  warm_epilogue(m.fold, nullptr);
  const int32_t corr = sparse4_accum<true>(m, q8, idx, nnz, acc);
  epi4_f32(acc, corr, m.fold, out);
}
void qsparse4_add(const QSparse4& m, const uint8_t* q8, const uint16_t* idx, int nnz, float* out) {
  alignas(64) int32_t acc[192];
  warm_epilogue(m.fold, out);
  const int32_t corr = sparse4_accum<true>(m, q8, idx, nnz, acc);
  epi4_add(acc, corr, m.fold, out);
}
void qsparse4_i32(const QSparse4& m, const uint8_t* q8, const uint16_t* idx, int nnz, int32_t* out) {  // test/debug
  alignas(64) int32_t acc[192];
  const int32_t corr = sparse4_accum<true>(m, q8, idx, nnz, acc);
  for (int r = 0; r < 192; r++) out[r] = acc[r] - corr;
}
void qsparse4_dense_f32(const QSparse4& m, const uint8_t* q8, float* out) {
  alignas(64) int32_t acc[192];
  warm_epilogue(m.fold, nullptr);
  const int32_t corr = dense4_accum(m, q8, acc);
  epi4_f32(acc, corr, m.fold, out);
}
void qsparse4_dense_add(const QSparse4& m, const uint8_t* q8, float* out) {
  alignas(64) int32_t acc[192];
  warm_epilogue(m.fold, out);
  const int32_t corr = dense4_accum(m, q8, acc);
  epi4_add(acc, corr, m.fold, out);
}
void qsparse4_dense_i32(const QSparse4& m, const uint8_t* q8, int32_t* out) {  // test/debug
  alignas(64) int32_t acc[192];
  const int32_t corr = dense4_accum(m, q8, acc);
  for (int r = 0; r < 192; r++) out[r] = acc[r] - corr;
}
void qsparse4_f32s(const QSparse4& m, const uint8_t* q8, const uint16_t* idx, int nnz, float s, float* out) {
  alignas(64) int32_t acc[192];
  warm_epilogue(m.fold, nullptr);
  const int32_t corr = sparse4_accum<true>(m, q8, idx, nnz, acc);
  epi4_f32s(acc, corr, m.fold, s, out);
}
void qsparse4_adds(const QSparse4& m, const uint8_t* q8, const uint16_t* idx, int nnz, float s, float* out) {
  alignas(64) int32_t acc[192];
  warm_epilogue(m.fold, out);
  const int32_t corr = sparse4_accum<true>(m, q8, idx, nnz, acc);
  epi4_adds(acc, corr, m.fold, s, out);
}
void qsparse4_dense_f32s(const QSparse4& m, const uint8_t* q8, float s, float* out) {
  alignas(64) int32_t acc[192];
  warm_epilogue(m.fold, nullptr);
  const int32_t corr = dense4_accum(m, q8, acc);
  epi4_f32s(acc, corr, m.fold, s, out);
}
void qsparse4_dense_adds(const QSparse4& m, const uint8_t* q8, float s, float* out) {
  alignas(64) int32_t acc[192];
  warm_epilogue(m.fold, out);
  const int32_t corr = dense4_accum(m, q8, acc);
  epi4_adds(acc, corr, m.fold, s, out);
}

}  // namespace avx512
}  // namespace opt
}  // namespace fx2
