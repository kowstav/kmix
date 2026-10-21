// qmat_dense_avx512.cpp -- AVX-512 VNNI variants of the dense qmat kernels (qmat_dense.h contracts,
// qmat_avx512.h declarations; TF_AVX512 fast path, 2026-09-19). Same arena layouts as the AVX2 kernels
// (QDense, QW8) plus the packed int4 + LUT arena QPackedCB (qmat.h section 4); bit-identical outputs.
//
// Core idea (8-row groups, d_in <= 256): one 64-byte weight load holds two rows' 32-column chunk
// ([row 2k | row 2k+1]); the 32-byte activation chunk is broadcast to both 256-bit halves ONCE per matmul
// (vbroadcasti64x4, NC zmm hoisted out of the group loop) and vpdpbusd(acc_k, act, w_k) accumulates
// u8*s8 groups of 4 straight into 16 int32 lanes. Per group: NC*4 dpbusd (memory-operand weights,
// nothing else in the loop), then a 13-uop shuffle/add tree reduces the 4 accumulators to the 8 row
// sums. The AVX2 path needs ~3x the uops for the same work (maddubs + paddw per 32 B, int16 widening
// every QMAT_WIDEN_CHUNKS chunks, vphaddd tree). Compiled with -mavx512f -mavx512bw -mavx512vl
// -mavx512vnni on top of the x86-64-v3 baseline; only reachable behind cpu_has_avx512_vnni().
#include "qmat_avx512.h"

#include <immintrin.h>

#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace fx2 {
namespace opt {
namespace avx512 {

namespace {

[[noreturn]] void die(const char* msg) {
  std::fprintf(stderr, "qmat[avx512]: %s\n", msg);
  std::exit(1);
}

// positions of set bits per 8-bit mask; unset slots hold 0 (in-range) — same
// table as qmat_dense.cpp (index lists are produced identically)
struct IdxLut {
  alignas(64) uint8_t t[256][8];
  IdxLut() {
    for (int m = 0; m < 256; m++) {
      int k = 0;
      for (int b = 0; b < 8; b++)
        if (m & (1 << b)) t[m][k++] = static_cast<uint8_t>(b);
      for (; k < 8; k++) t[m][k] = 0;
    }
  }
};
const IdxLut g_idxlut;

constexpr int PFN_DEFAULT = 4;  // prefetch lines per 256 B chunk (2 KB ahead), as the AVX2 kernels

// ---------------------------------------------------------------------------
// reductions. A_k lanes 0-7 hold 4-column partial sums of row 2k, lanes 8-15
// of row 2k+1 (k = 0..3). Integer adds: exact in any order.
// ---------------------------------------------------------------------------
// per 128-bit lane j of the result: [sum(A0 lane j), sum(A1 lane j), sum(A2 lane j), sum(A3 lane j)]
inline __m512i red_stage(__m512i A0, __m512i A1, __m512i A2, __m512i A3) {
  const __m512i c0 = _mm512_add_epi32(_mm512_unpacklo_epi32(A0, A1), _mm512_unpackhi_epi32(A0, A1));
  const __m512i c1 = _mm512_add_epi32(_mm512_unpacklo_epi32(A2, A3), _mm512_unpackhi_epi32(A2, A3));
  return _mm512_add_epi32(_mm512_unpacklo_epi64(c0, c1), _mm512_unpackhi_epi64(c0, c1));
}
// -> [r0 r1 r2 r3 r4 r5 r6 r7] (natural row order of the 8-row group)
inline __m256i reduce_rows8(__m512i A0, __m512i A1, __m512i A2, __m512i A3) {
  const __m512i e = red_stage(A0, A1, A2, A3);
  // lanes j=0,1 -> rows 0,2,4,6 halves; j=2,3 -> rows 1,3,5,7 halves: add adjacent 128-bit lanes
  const __m512i f = _mm512_add_epi32(e, _mm512_shuffle_i32x4(e, e, _MM_SHUFFLE(2, 3, 0, 1)));
  const __m512i idx = _mm512_setr_epi32(0, 8, 1, 9, 2, 10, 3, 11, 0, 0, 0, 0, 0, 0, 0, 0);
  return _mm512_castsi512_si256(_mm512_permutexvar_epi32(idx, f));
}
// full 16-lane sums: -> [sum A0, sum A1, sum A2, sum A3]
inline __m128i reduce_full4(__m512i A0, __m512i A1, __m512i A2, __m512i A3) {
  const __m512i e = red_stage(A0, A1, A2, A3);
  __m512i t = _mm512_add_epi32(e, _mm512_shuffle_i32x4(e, e, _MM_SHUFFLE(1, 0, 3, 2)));
  t = _mm512_add_epi32(t, _mm512_shuffle_i32x4(t, t, _MM_SHUFFLE(2, 3, 0, 1)));
  return _mm512_castsi512_si128(t);
}

inline __m512i bcast32(const uint8_t* p) {  // [32 B | same 32 B]
  return _mm512_broadcast_i64x4(_mm256_load_si256(reinterpret_cast<const __m256i*>(p)));
}

// ---------------------------------------------------------------------------
// epilogue functors — the SAME fp32 op sequences as qmat_dense.cpp
// (cvtepi32_ps, mul, [mul s], [add residual]; never fused)
// ---------------------------------------------------------------------------
struct EpiF32 {
  float* out;
  inline void operator()(int g, __m256i sums, __m256 scl) {
    _mm256_storeu_ps(out + 8 * g, _mm256_mul_ps(_mm256_cvtepi32_ps(sums), scl));
  }
  inline void g4(int g, __m128i sums, __m128 scl) {
    _mm_storeu_ps(out + 4 * g, _mm_mul_ps(_mm_cvtepi32_ps(sums), scl));
  }
};

struct EpiAdd {
  float* out;
  inline void operator()(int g, __m256i sums, __m256 scl) {
    const __m256 t = _mm256_mul_ps(_mm256_cvtepi32_ps(sums), scl);
    _mm256_storeu_ps(out + 8 * g, _mm256_add_ps(_mm256_loadu_ps(out + 8 * g), t));
  }
  inline void g4(int g, __m128i sums, __m128 scl) {
    const __m128 t = _mm_mul_ps(_mm_cvtepi32_ps(sums), scl);
    _mm_storeu_ps(out + 4 * g, _mm_add_ps(_mm_loadu_ps(out + 4 * g), t));
  }
};

struct EpiF32S {
  float* out;
  __m256 vs;
  inline void operator()(int g, __m256i sums, __m256 scl) {
    const __m256 y = _mm256_mul_ps(_mm256_cvtepi32_ps(sums), scl);
    _mm256_storeu_ps(out + 8 * g, _mm256_mul_ps(y, vs));
  }
  inline void g4(int g, __m128i sums, __m128 scl) {
    const __m128 y = _mm_mul_ps(_mm_cvtepi32_ps(sums), scl);
    _mm_storeu_ps(out + 4 * g, _mm_mul_ps(y, _mm256_castps256_ps128(vs)));
  }
};

struct EpiAddS {
  float* out;
  __m256 vs;
  inline void operator()(int g, __m256i sums, __m256 scl) {
    __m256 t = _mm256_mul_ps(_mm256_cvtepi32_ps(sums), scl);
    t = _mm256_mul_ps(t, vs);
    _mm256_storeu_ps(out + 8 * g, _mm256_add_ps(_mm256_loadu_ps(out + 8 * g), t));
  }
  inline void g4(int g, __m128i sums, __m128 scl) {
    __m128 t = _mm_mul_ps(_mm_cvtepi32_ps(sums), scl);
    t = _mm_mul_ps(t, _mm256_castps256_ps128(vs));
    _mm_storeu_ps(out + 4 * g, _mm_add_ps(_mm_loadu_ps(out + 4 * g), t));
  }
};

// (g) phase 1: h = max((float(dot)*scale)*s, 0)^2 stored, running max of h
struct EpiRelu2S {
  float* out;
  __m256 vs;
  __m256 vmax;
  inline void operator()(int g, __m256i sums, __m256 scl) {
    __m256 y = _mm256_mul_ps(_mm256_cvtepi32_ps(sums), scl);
    y = _mm256_max_ps(_mm256_mul_ps(y, vs), _mm256_setzero_ps());
    const __m256 h = _mm256_mul_ps(y, y);
    _mm256_storeu_ps(out + 8 * g, h);
    vmax = _mm256_max_ps(vmax, h);
  }
  inline void g4(int g, __m128i sums, __m128 scl) {
    __m128 y = _mm_mul_ps(_mm_cvtepi32_ps(sums), scl);
    y = _mm_max_ps(_mm_mul_ps(y, _mm256_castps256_ps128(vs)), _mm_setzero_ps());
    const __m128 h = _mm_mul_ps(y, y);
    _mm_storeu_ps(out + 4 * g, h);
    vmax = _mm256_max_ps(vmax, _mm256_insertf128_ps(_mm256_setzero_ps(), h, 0));
  }
};

// (h) phase 1: y = (float(dot)*scale)*s stored, running max of |y|
struct EpiF32SAbsMax {
  float* out;
  __m256 vs;
  __m256 vmax;
  inline void operator()(int g, __m256i sums, __m256 scl) {
    __m256 y = _mm256_mul_ps(_mm256_cvtepi32_ps(sums), scl);
    y = _mm256_mul_ps(y, vs);
    _mm256_storeu_ps(out + 8 * g, y);
    vmax = _mm256_max_ps(vmax, _mm256_andnot_ps(_mm256_set1_ps(-0.0f), y));
  }
  inline void g4(int g, __m128i sums, __m128 scl) {
    __m128 y = _mm_mul_ps(_mm_cvtepi32_ps(sums), scl);
    y = _mm_mul_ps(y, _mm256_castps256_ps128(vs));
    _mm_storeu_ps(out + 4 * g, y);
    const __m128 a = _mm_andnot_ps(_mm_set1_ps(-0.0f), y);
    vmax = _mm256_max_ps(vmax, _mm256_insertf128_ps(_mm256_setzero_ps(), a, 0));
  }
};

struct EpiI32 {
  int32_t* out;
  inline void operator()(int g, __m256i sums, __m256) {
    _mm256_storeu_si256(reinterpret_cast<__m256i*>(out + 8 * g), sums);
  }
  inline void g4(int g, __m128i sums, __m128) {
    _mm_storeu_si128(reinterpret_cast<__m128i*>(out + 4 * g), sums);
  }
};

inline float hmax256_(__m256 v) {  // exact in any order
  __m128 lo = _mm256_castps256_ps128(v);
  const __m128 hi = _mm256_extractf128_ps(v, 1);
  lo = _mm_max_ps(lo, hi);
  lo = _mm_max_ps(lo, _mm_movehl_ps(lo, lo));
  lo = _mm_max_ss(lo, _mm_movehdup_ps(lo));
  return _mm_cvtss_f32(lo);
}
inline float dyn_scale_from_amax_(float amax) {
  if (amax < 1e-12f) amax = 1e-12f;
  return amax / 127.0f;
}

// ---------------------------------------------------------------------------
// core: 8-row groups, d_in <= 256 (NC chunks of 32 columns; GB = 64 + 256*NC)
// ---------------------------------------------------------------------------
template <int NC, int PFN, class Epi>
inline void run_g8(const QDense& m, const uint8_t* act, Epi& epi) {
  __m512i av[NC];
  for (int c = 0; c < NC; c++) av[c] = bcast32(act + 32 * c);
  const uint8_t* gp = m.arena;
  constexpr ptrdiff_t GB = 64 + NC * 256;
  constexpr bool SPLIT = NC >= 4;  // even/odd chunk accumulators halve the dependency chain
  const int ng = m.ngroups;
  for (int g = 0; g < ng; g++, gp += GB) {
    const __m512i* w = reinterpret_cast<const __m512i*>(gp + 64);
    __m512i a0 = _mm512_setzero_si512(), a1 = a0, a2 = a0, a3 = a0;
    __m512i b0 = a0, b1 = a0, b2 = a0, b3 = a0;
#pragma GCC unroll 8
    for (int c = 0; c < NC; c++) {
      for (int k = 0; k < PFN; k++)
        _mm_prefetch(reinterpret_cast<const char*>(gp) + c * 256 + 2048 + 64 * k, _MM_HINT_T0);
      const __m512i* wc = w + 4 * c;
      if (SPLIT && (c & 1)) {
        b0 = _mm512_dpbusd_epi32(b0, av[c], _mm512_load_si512(wc + 0));
        b1 = _mm512_dpbusd_epi32(b1, av[c], _mm512_load_si512(wc + 1));
        b2 = _mm512_dpbusd_epi32(b2, av[c], _mm512_load_si512(wc + 2));
        b3 = _mm512_dpbusd_epi32(b3, av[c], _mm512_load_si512(wc + 3));
      } else {
        a0 = _mm512_dpbusd_epi32(a0, av[c], _mm512_load_si512(wc + 0));
        a1 = _mm512_dpbusd_epi32(a1, av[c], _mm512_load_si512(wc + 1));
        a2 = _mm512_dpbusd_epi32(a2, av[c], _mm512_load_si512(wc + 2));
        a3 = _mm512_dpbusd_epi32(a3, av[c], _mm512_load_si512(wc + 3));
      }
    }
    if (SPLIT) {
      a0 = _mm512_add_epi32(a0, b0);
      a1 = _mm512_add_epi32(a1, b1);
      a2 = _mm512_add_epi32(a2, b2);
      a3 = _mm512_add_epi32(a3, b3);
    }
    __m256i sums = reduce_rows8(a0, a1, a2, a3);
    sums = _mm256_sub_epi32(sums, _mm256_load_si256(reinterpret_cast<const __m256i*>(gp)));
    epi(g, sums, _mm256_load_ps(reinterpret_cast<const float*>(gp + 32)));
  }
}

// ---------------------------------------------------------------------------
// core: 4-row groups, d_in == 768 (24 chunks; GB = 32 + 24*128 = 3104).
// NOTE: 3104 = 32 mod 64, so every other group's weights are only 32-byte
// aligned -> unaligned 512-bit loads (free when the address is aligned).
// Two groups per iteration share each activation broadcast and fill the
// 8-row reduction; an odd trailing group uses the 4-row epilogue.
// ---------------------------------------------------------------------------
template <int PFN, class Epi>
inline void run_g4_768(const QDense& m, const uint8_t* act, Epi& epi) {
  const uint8_t* gp = m.arena;
  constexpr ptrdiff_t GB = 32 + 24 * 128;
  const int ng = m.ngroups;
  int g = 0;
  for (; g + 1 < ng; g += 2, gp += 2 * GB) {
    const __m512i* w0 = reinterpret_cast<const __m512i*>(gp + 32);
    const __m512i* w1 = reinterpret_cast<const __m512i*>(gp + GB + 32);
    __m512i a0 = _mm512_setzero_si512(), a1 = a0, a2 = a0, a3 = a0;
    __m512i b0 = a0, b1 = a0, b2 = a0, b3 = a0;
#pragma GCC unroll 4
    for (int c = 0; c < 24; c++) {
      if (PFN) {
        _mm_prefetch(reinterpret_cast<const char*>(gp) + 32 + c * 128 + 2048, _MM_HINT_T0);
        _mm_prefetch(reinterpret_cast<const char*>(gp) + GB + 32 + c * 128 + 2048, _MM_HINT_T0);
        if (PFN > 1) {
          _mm_prefetch(reinterpret_cast<const char*>(gp) + 32 + c * 128 + 2112, _MM_HINT_T0);
          _mm_prefetch(reinterpret_cast<const char*>(gp) + GB + 32 + c * 128 + 2112, _MM_HINT_T0);
        }
      }
      const __m512i av = bcast32(act + 32 * c);
      if (c & 1) {
        b0 = _mm512_dpbusd_epi32(b0, av, _mm512_loadu_si512(w0 + 2 * c));
        b1 = _mm512_dpbusd_epi32(b1, av, _mm512_loadu_si512(w0 + 2 * c + 1));
        b2 = _mm512_dpbusd_epi32(b2, av, _mm512_loadu_si512(w1 + 2 * c));
        b3 = _mm512_dpbusd_epi32(b3, av, _mm512_loadu_si512(w1 + 2 * c + 1));
      } else {
        a0 = _mm512_dpbusd_epi32(a0, av, _mm512_loadu_si512(w0 + 2 * c));
        a1 = _mm512_dpbusd_epi32(a1, av, _mm512_loadu_si512(w0 + 2 * c + 1));
        a2 = _mm512_dpbusd_epi32(a2, av, _mm512_loadu_si512(w1 + 2 * c));
        a3 = _mm512_dpbusd_epi32(a3, av, _mm512_loadu_si512(w1 + 2 * c + 1));
      }
    }
    a0 = _mm512_add_epi32(a0, b0);
    a1 = _mm512_add_epi32(a1, b1);
    a2 = _mm512_add_epi32(a2, b2);
    a3 = _mm512_add_epi32(a3, b3);
    __m256i sums = reduce_rows8(a0, a1, a2, a3);  // [g rows 0-3 | g+1 rows 0-3]
    const __m256i corr = _mm256_set_m128i(_mm_load_si128(reinterpret_cast<const __m128i*>(gp + GB)),
                                          _mm_load_si128(reinterpret_cast<const __m128i*>(gp)));
    const __m256 scl = _mm256_set_m128(_mm_load_ps(reinterpret_cast<const float*>(gp + GB + 16)),
                                       _mm_load_ps(reinterpret_cast<const float*>(gp + 16)));
    sums = _mm256_sub_epi32(sums, corr);
    epi(g >> 1, sums, scl);  // out + 8*(g/2) == out + 4*g
  }
  if (g < ng) {  // odd trailing group
    const __m512i* w0 = reinterpret_cast<const __m512i*>(gp + 32);
    __m512i a0 = _mm512_setzero_si512(), a1 = a0, b0 = a0, b1 = a0;
    for (int c = 0; c < 24; c++) {
      const __m512i av = bcast32(act + 32 * c);
      if (c & 1) {
        b0 = _mm512_dpbusd_epi32(b0, av, _mm512_loadu_si512(w0 + 2 * c));
        b1 = _mm512_dpbusd_epi32(b1, av, _mm512_loadu_si512(w0 + 2 * c + 1));
      } else {
        a0 = _mm512_dpbusd_epi32(a0, av, _mm512_loadu_si512(w0 + 2 * c));
        a1 = _mm512_dpbusd_epi32(a1, av, _mm512_loadu_si512(w0 + 2 * c + 1));
      }
    }
    a0 = _mm512_add_epi32(a0, b0);
    a1 = _mm512_add_epi32(a1, b1);
    const __m256i s8 = reduce_rows8(a0, a1, _mm512_setzero_si512(), _mm512_setzero_si512());
    __m128i sums = _mm256_castsi256_si128(s8);
    sums = _mm_sub_epi32(sums, _mm_load_si128(reinterpret_cast<const __m128i*>(gp)));
    epi.g4(g, sums, _mm_load_ps(reinterpret_cast<const float*>(gp + 16)));
  }
}

// -DQMAT_AVX512_ALL_SHAPES=1 (tests): also the shapes the production model never runs through the AVX-512
// QDense kernels (205/224-in prior projection = QSparse4/QW8 in the model, 768-in = QSparse4), keeping the
// production objects small (the switch is instantiated in every public kernel).
#ifndef QMAT_AVX512_ALL_SHAPES
#define QMAT_AVX512_ALL_SHAPES 0
#endif
template <int PFN, class Epi>
inline void dispatch(const QDense& m, const uint8_t* act, Epi& epi) {
  switch (m.d_in) {
    case 64:
      run_g8<2, PFN>(m, act, epi);
      break;
    case 192:
      run_g8<6, PFN>(m, act, epi);
      break;
#if QMAT_AVX512_ALL_SHAPES
    case 205:
    case 224:
      run_g8<7, PFN>(m, act, epi);
      break;
    case 768:
      run_g4_768<(PFN > 0 ? 2 : 0)>(m, act, epi);
      break;
#endif
    default:
      die("unsupported d_in");
  }
}

// ---------------------------------------------------------------------------
// phase-2 passes of the quantizing epilogues — verbatim copies of the AVX2
// code (per-lane ops; bit-identical by construction)
// ---------------------------------------------------------------------------
inline int relu2_pack_idx(int ngroups, int rows_padded, const float* y, float s, uint8_t* q_out, uint16_t* idx_out) {
  const __m256 vs = _mm256_set1_ps(s);
  const __m256 v127 = _mm256_set1_ps(127.0f);
  const int ng2 = ngroups & ~1;
  for (int g = 0; g < ng2; g += 2) {
    const __m256 t0 = _mm256_div_ps(_mm256_load_ps(y + 8 * g), vs);  // IEEE div
    const __m256 t1 = _mm256_div_ps(_mm256_load_ps(y + 8 * g + 8), vs);
    const __m256i q0 = _mm256_cvtps_epi32(_mm256_min_ps(t0, v127));  // rte
    const __m256i q1 = _mm256_cvtps_epi32(_mm256_min_ps(t1, v127));
    __m256i q16 = _mm256_packs_epi32(q0, q1);
    q16 = _mm256_permute4x64_epi64(q16, _MM_SHUFFLE(3, 1, 2, 0));
    const __m128i q8v = _mm_packus_epi16(_mm256_castsi256_si128(q16), _mm256_extracti128_si256(q16, 1));
    _mm_storeu_si128(reinterpret_cast<__m128i*>(q_out + 8 * g), q8v);
  }
  if (ngroups & 1) {
    const int g = ngroups - 1;
    const __m256 t = _mm256_div_ps(_mm256_load_ps(y + 8 * g), vs);
    const __m256i q = _mm256_cvtps_epi32(_mm256_min_ps(t, v127));
    const __m128i q16 = _mm_packs_epi32(_mm256_castsi256_si128(q), _mm256_extracti128_si256(q, 1));
    _mm_storel_epi64(reinterpret_cast<__m128i*>(q_out + 8 * g), _mm_packus_epi16(q16, q16));
  }
  int nnz = 0;
  const int nblk = rows_padded / 32;
  for (int b = 0; b < nblk; b++) {
    const __m256i v = _mm256_load_si256(reinterpret_cast<const __m256i*>(q_out + 32 * b));
    const uint32_t mz = static_cast<uint32_t>(_mm256_movemask_epi8(_mm256_cmpeq_epi8(v, _mm256_setzero_si256())));
    const uint32_t mk = ~mz;
    for (int k = 0; k < 4; k++) {
      const uint32_t m8 = (mk >> (8 * k)) & 0xFF;
      const __m128i lut = _mm_loadl_epi64(reinterpret_cast<const __m128i*>(g_idxlut.t[m8]));
      const __m128i i16 = _mm_add_epi16(_mm_cvtepu8_epi16(lut), _mm_set1_epi16(static_cast<short>(32 * b + 8 * k)));
      _mm_storeu_si128(reinterpret_cast<__m128i*>(idx_out + nnz), i16);
      nnz += __builtin_popcount(m8);
    }
  }
  for (int r = rows_padded & ~31; r < rows_padded; r++)
    if (q_out[r]) idx_out[nnz++] = static_cast<uint16_t>(r);
  return nnz;
}

// (c) phase 2a: relu^2 + quantize on the stored y (fold*float(dot)), then the index scan
inline int relu2q_phase2(int ngroups, int rows_padded, const float* y, float s_next, uint8_t* q_out, uint16_t* idx_out) {
  const __m256 vs = _mm256_set1_ps(s_next);
  const __m256 v127 = _mm256_set1_ps(127.0f);
  const __m256 vz = _mm256_setzero_ps();
  const int ng2 = ngroups & ~1;
  for (int g = 0; g < ng2; g += 2) {
    const __m256 y0 = _mm256_max_ps(_mm256_load_ps(y + 8 * g), vz);
    const __m256 y1 = _mm256_max_ps(_mm256_load_ps(y + 8 * g + 8), vz);
    const __m256 t0 = _mm256_div_ps(_mm256_mul_ps(y0, y0), vs);
    const __m256 t1 = _mm256_div_ps(_mm256_mul_ps(y1, y1), vs);
    const __m256i q0 = _mm256_cvtps_epi32(_mm256_min_ps(t0, v127));
    const __m256i q1 = _mm256_cvtps_epi32(_mm256_min_ps(t1, v127));
    __m256i q16 = _mm256_packs_epi32(q0, q1);
    q16 = _mm256_permute4x64_epi64(q16, _MM_SHUFFLE(3, 1, 2, 0));
    const __m128i q8v = _mm_packus_epi16(_mm256_castsi256_si128(q16), _mm256_extracti128_si256(q16, 1));
    _mm_storeu_si128(reinterpret_cast<__m128i*>(q_out + 8 * g), q8v);
  }
  if (ngroups & 1) {
    const int g = ngroups - 1;
    const __m256 yv = _mm256_max_ps(_mm256_load_ps(y + 8 * g), vz);
    const __m256 t = _mm256_div_ps(_mm256_mul_ps(yv, yv), vs);
    const __m256i q = _mm256_cvtps_epi32(_mm256_min_ps(t, v127));
    const __m128i q16 = _mm_packs_epi32(_mm256_castsi256_si128(q), _mm256_extracti128_si256(q, 1));
    _mm_storel_epi64(reinterpret_cast<__m128i*>(q_out + 8 * g), _mm_packus_epi16(q16, q16));
  }
  int nnz = 0;
  const int nblk = rows_padded / 32;
  for (int b = 0; b < nblk; b++) {
    const __m256i v = _mm256_load_si256(reinterpret_cast<const __m256i*>(q_out + 32 * b));
    const uint32_t mz = static_cast<uint32_t>(_mm256_movemask_epi8(_mm256_cmpeq_epi8(v, _mm256_setzero_si256())));
    const uint32_t mk = ~mz;
    for (int k = 0; k < 4; k++) {
      const uint32_t m8 = (mk >> (8 * k)) & 0xFF;
      const __m128i lut = _mm_loadl_epi64(reinterpret_cast<const __m128i*>(g_idxlut.t[m8]));
      const __m128i i16 = _mm_add_epi16(_mm_cvtepu8_epi16(lut), _mm_set1_epi16(static_cast<short>(32 * b + 8 * k)));
      _mm_storeu_si128(reinterpret_cast<__m128i*>(idx_out + nnz), i16);
      nnz += __builtin_popcount(m8);
    }
  }
  for (int r = rows_padded & ~31; r < rows_padded; r++)
    if (q_out[r]) idx_out[nnz++] = static_cast<uint16_t>(r);
  return nnz;
}

// (d)/(h) phase 2: biased quantize of the stored y by s
inline void quant_bias_phase2(int ngroups, int rows_padded, const float* y, float s, uint8_t* q_out) {
  (void)rows_padded;
  const __m256 vs = _mm256_set1_ps(s);
  const __m256 vlo = _mm256_set1_ps(-128.0f);
  const __m256 vhi = _mm256_set1_ps(127.0f);
  const __m256i v128 = _mm256_set1_epi32(128);
  for (int g = 0; g < ngroups; g++) {
    __m256 t = _mm256_div_ps(_mm256_load_ps(y + 8 * g), vs);
    t = _mm256_min_ps(_mm256_max_ps(t, vlo), vhi);
    const __m256i q = _mm256_add_epi32(_mm256_cvtps_epi32(t), v128);
    const __m128i q16 = _mm_packs_epi32(_mm256_castsi256_si128(q), _mm256_extracti128_si256(q, 1));
    _mm_storel_epi64(reinterpret_cast<__m128i*>(q_out + 8 * g), _mm_packus_epi16(q16, q16));
  }
}

}  // namespace

// ---------------------------------------------------------------------------
// public dense kernels (QDense arena). The production model dispatches only
// qgemv_f32 / qgemv_f32s on the 192x64 gate-down sites here (every other dense
// site uses the QPackedCB arena below); the rest are linked out by
// --gc-sections and exist for test_avx512 and as complete twins of qmat_dense.h.
// ---------------------------------------------------------------------------
void qgemv_f32(const QDense& m, const uint8_t* act, float* out) {
  EpiF32 e{out};
  dispatch<PFN_DEFAULT>(m, act, e);
}

void qgemv_f32_nopf(const QDense& m, const uint8_t* act, float* out) {
  EpiF32 e{out};
  dispatch<0>(m, act, e);
}

void qgemv_add(const QDense& m, const uint8_t* act, float* out) {
  EpiAdd e{out};
  dispatch<PFN_DEFAULT>(m, act, e);
}

void qgemv_f32s(const QDense& m, const uint8_t* act, float s, float* out) {
  EpiF32S e{out, _mm256_set1_ps(s)};
  dispatch<PFN_DEFAULT>(m, act, e);
}

void qgemv_adds(const QDense& m, const uint8_t* act, float s, float* out) {
  EpiAddS e{out, _mm256_set1_ps(s)};
  dispatch<PFN_DEFAULT>(m, act, e);
}

void qgemv_i32(const QDense& m, const uint8_t* act, int32_t* out) {
  EpiI32 e{out};
  dispatch<PFN_DEFAULT>(m, act, e);
}

int qgemv_relu2q(const QDense& m, const uint8_t* act, float s_next, uint8_t* q_out, uint16_t* idx_out) {
  if (m.d_in != 192) die("relu2q epilogue requires d_in==192");
  if (m.rows_padded > 768) die("relu2q epilogue requires d_out<=768");
  alignas(64) float y[768];
  EpiF32 e{y};
  run_g8<6, PFN_DEFAULT>(m, act, e);
  return relu2q_phase2(m.ngroups, m.rows_padded, y, s_next, q_out, idx_out);
}

void qgemv_quant_bias(const QDense& m, const uint8_t* act, float s_next, uint8_t* q_out) {
  if (m.d_in != 192) die("quant_bias epilogue requires d_in==192");
  if (m.rows_padded > 768) die("quant_bias epilogue requires d_out<=768");
  alignas(64) float y[768];
  EpiF32 e{y};
  run_g8<6, PFN_DEFAULT>(m, act, e);
  quant_bias_phase2(m.ngroups, m.rows_padded, y, s_next, q_out);
}

int qgemv_relu2q_dyn(const QDense& m, const uint8_t* act, float s_in, uint8_t* q_out, uint16_t* idx_out,
                     float* s_next) {
  if (m.d_in != 192) die("relu2q_dyn epilogue requires d_in==192");
  if (m.rows_padded > 768) die("relu2q_dyn epilogue requires d_out<=768");
  alignas(64) float h[768];
  EpiRelu2S e{h, _mm256_set1_ps(s_in), _mm256_setzero_ps()};
  run_g8<6, PFN_DEFAULT>(m, act, e);
  const float s_h = dyn_scale_from_amax_(hmax256_(e.vmax));
  *s_next = s_h;
  return relu2_pack_idx(m.ngroups, m.rows_padded, h, s_h, q_out, idx_out);
}

float qgemv_quant_bias_dyn(const QDense& m, const uint8_t* act, float s_in, uint8_t* q_out) {
  if (m.d_in != 192) die("quant_bias_dyn epilogue requires d_in==192");
  if (m.rows_padded > 768) die("quant_bias_dyn epilogue requires d_out<=768");
  alignas(64) float y[768];
  EpiF32SAbsMax e{y, _mm256_set1_ps(s_in), _mm256_setzero_ps()};
  run_g8<6, PFN_DEFAULT>(m, act, e);
  const float s_y = dyn_scale_from_amax_(hmax256_(e.vmax));
  quant_bias_phase2(m.ngroups, m.rows_padded, y, s_y, q_out);
  return s_y;
}

// ---------------------------------------------------------------------------
// 8-bit small matmuls (QW8): vpdpbusd over the row-major int8 weights,
// 4 rows per iteration, transposed full reduction -> 4 dots.
// ---------------------------------------------------------------------------
void qw8_f32(const QW8& m, const uint8_t* act, float* out) {
  const int S = m.stride;  // multiple of 32
  if (S > 256 || (S & 31)) die("qw8: unsupported stride");
  const int n64 = S >> 6;
  const bool half = (S & 63) != 0;
  const __mmask64 tail = 0x00000000FFFFFFFFull;
  __m512i a[4];
  for (int j = 0; j < 4; j++)
    a[j] = j < n64 ? _mm512_loadu_si512(act + 64 * j)
                   : (j == n64 && half ? _mm512_maskz_loadu_epi8(tail, act + 64 * j) : _mm512_setzero_si512());
  for (int o = 0; o < m.rows_padded; o += 4) {  // rows_padded is a multiple of 8
    const int8_t* w0 = m.w + static_cast<size_t>(o) * S;
    const int8_t* w1 = w0 + S;
    const int8_t* w2 = w1 + S;
    const int8_t* w3 = w2 + S;
    __m512i c0 = _mm512_setzero_si512(), c1 = c0, c2 = c0, c3 = c0;
    for (int j = 0; j < n64; j++) {
      c0 = _mm512_dpbusd_epi32(c0, a[j], _mm512_loadu_si512(w0 + 64 * j));
      c1 = _mm512_dpbusd_epi32(c1, a[j], _mm512_loadu_si512(w1 + 64 * j));
      c2 = _mm512_dpbusd_epi32(c2, a[j], _mm512_loadu_si512(w2 + 64 * j));
      c3 = _mm512_dpbusd_epi32(c3, a[j], _mm512_loadu_si512(w3 + 64 * j));
    }
    if (half) {
      c0 = _mm512_dpbusd_epi32(c0, a[n64], _mm512_maskz_loadu_epi8(tail, w0 + 64 * n64));
      c1 = _mm512_dpbusd_epi32(c1, a[n64], _mm512_maskz_loadu_epi8(tail, w1 + 64 * n64));
      c2 = _mm512_dpbusd_epi32(c2, a[n64], _mm512_maskz_loadu_epi8(tail, w2 + 64 * n64));
      c3 = _mm512_dpbusd_epi32(c3, a[n64], _mm512_maskz_loadu_epi8(tail, w3 + 64 * n64));
    }
    __m128i s4 = reduce_full4(c0, c1, c2, c3);
    s4 = _mm_sub_epi32(s4, _mm_loadu_si128(reinterpret_cast<const __m128i*>(m.corr + o)));
    _mm_storeu_ps(out + o, _mm_mul_ps(_mm_loadu_ps(m.fold + o), _mm_cvtepi32_ps(s4)));
  }
  for (int o = m.d_out; o < m.rows_padded; o++) out[o] = 0.0f;  // pad rows: +0.0f exactly as the AVX2 kernel
}

// ---------------------------------------------------------------------------
// packed int4 + LUT arena (QPackedCB): 8-row groups [8 corr | 8 scale |
// npair x 8 rows x 32 B nibbles]. Per pair p and row pair k: one 64-byte load
// = [row 2k | row 2k+1] nibbles; low nibbles -> cols [64p, 64p+32), high ->
// [64p+32, 64p+64); each nibble (level index) is mapped through the LUT
// (vpshufb, per 128-bit lane) to the signed int8 weight, which is the s8
// operand of vpdpbusd; the u8 operand is the activation chunk broadcast to
// both halves. Then exactly the QDense reduction / epilogues.
// Per 64 B of arena: 1 load, 1 and, 1 shift+and, 2 vpshufb, 2 dpbusd = 128 MACs.
// ---------------------------------------------------------------------------
namespace {
template <int NPAIR, int PFN, class Epi>
inline void run_pcb(const QPackedCB& m, const uint8_t* act, Epi& epi) {
  const __m512i m0F = _mm512_set1_epi8(0x0F);
  const __m512i lut = _mm512_load_si512(m.lut);
  constexpr bool HOIST = NPAIR <= 4;  // 2 act registers per pair
  __m512i alo[HOIST ? NPAIR : 1], ahi[HOIST ? NPAIR : 1];
  if (HOIST)
    for (int p = 0; p < NPAIR; p++) {
      alo[p] = bcast32(act + 64 * p);
      ahi[p] = bcast32(act + 64 * p + 32);
    }
  const uint8_t* gp = m.arena;
  constexpr ptrdiff_t GB = 64 + 256 * NPAIR;
  const int ng = m.ngroups;
  for (int g = 0; g < ng; g++, gp += GB) {
    const __m512i* w = reinterpret_cast<const __m512i*>(gp + 64);
    __m512i a0 = _mm512_setzero_si512(), a1 = a0, a2 = a0, a3 = a0;  // low-nibble columns
    __m512i b0 = a0, b1 = a0, b2 = a0, b3 = a0;                      // high-nibble columns
#pragma GCC unroll 4
    for (int p = 0; p < NPAIR; p++) {
      for (int k = 0; k < PFN; k++)
        _mm_prefetch(reinterpret_cast<const char*>(gp) + p * 256 + 2048 + 64 * k, _MM_HINT_T0);
      const __m512i vlo = HOIST ? alo[p] : bcast32(act + 64 * p);
      const __m512i vhi = HOIST ? ahi[p] : bcast32(act + 64 * p + 32);
      const __m512i x0 = _mm512_load_si512(w + 4 * p + 0);
      const __m512i x1 = _mm512_load_si512(w + 4 * p + 1);
      const __m512i x2 = _mm512_load_si512(w + 4 * p + 2);
      const __m512i x3 = _mm512_load_si512(w + 4 * p + 3);
      a0 = _mm512_dpbusd_epi32(a0, vlo, _mm512_shuffle_epi8(lut, _mm512_and_si512(x0, m0F)));
      a1 = _mm512_dpbusd_epi32(a1, vlo, _mm512_shuffle_epi8(lut, _mm512_and_si512(x1, m0F)));
      a2 = _mm512_dpbusd_epi32(a2, vlo, _mm512_shuffle_epi8(lut, _mm512_and_si512(x2, m0F)));
      a3 = _mm512_dpbusd_epi32(a3, vlo, _mm512_shuffle_epi8(lut, _mm512_and_si512(x3, m0F)));
      b0 = _mm512_dpbusd_epi32(b0, vhi, _mm512_shuffle_epi8(lut, _mm512_and_si512(_mm512_srli_epi16(x0, 4), m0F)));
      b1 = _mm512_dpbusd_epi32(b1, vhi, _mm512_shuffle_epi8(lut, _mm512_and_si512(_mm512_srli_epi16(x1, 4), m0F)));
      b2 = _mm512_dpbusd_epi32(b2, vhi, _mm512_shuffle_epi8(lut, _mm512_and_si512(_mm512_srli_epi16(x2, 4), m0F)));
      b3 = _mm512_dpbusd_epi32(b3, vhi, _mm512_shuffle_epi8(lut, _mm512_and_si512(_mm512_srli_epi16(x3, 4), m0F)));
    }
    a0 = _mm512_add_epi32(a0, b0);
    a1 = _mm512_add_epi32(a1, b1);
    a2 = _mm512_add_epi32(a2, b2);
    a3 = _mm512_add_epi32(a3, b3);
    __m256i sums = reduce_rows8(a0, a1, a2, a3);
    sums = _mm256_sub_epi32(sums, _mm256_load_si256(reinterpret_cast<const __m256i*>(gp)));
    epi(g, sums, _mm256_load_ps(reinterpret_cast<const float*>(gp + 32)));
  }
}

// the model builds QPackedCB arenas for its 192-in sites only (npair 3; the 64-in gate-down matrices stay
// QDense, see arena_build.cpp); the other widths are test-only shapes (QMAT_AVX512_ALL_SHAPES)
template <int PFN, class Epi>
inline void dispatch_pcb(const QPackedCB& m, const uint8_t* act, Epi& epi) {
  switch (m.npair) {
    case 3:
      run_pcb<3, PFN>(m, act, epi);
      break;
#if QMAT_AVX512_ALL_SHAPES
    case 1:
      run_pcb<1, PFN>(m, act, epi);
      break;
    case 4:  // 205/224-in
      run_pcb<4, PFN>(m, act, epi);
      break;
    case 12:
      run_pcb<12, PFN>(m, act, epi);
      break;
#endif
    default:
      die("unsupported packedcb npair");
  }
}
}  // namespace

void qgemv_pcb_f32(const QPackedCB& m, const uint8_t* act, float* out) {
  EpiF32 e{out};
  dispatch_pcb<PFN_DEFAULT>(m, act, e);
}
void qgemv_pcb_add(const QPackedCB& m, const uint8_t* act, float* out) {
  EpiAdd e{out};
  dispatch_pcb<PFN_DEFAULT>(m, act, e);
}
void qgemv_pcb_f32s(const QPackedCB& m, const uint8_t* act, float s, float* out) {
  EpiF32S e{out, _mm256_set1_ps(s)};
  dispatch_pcb<PFN_DEFAULT>(m, act, e);
}
void qgemv_pcb_adds(const QPackedCB& m, const uint8_t* act, float s, float* out) {
  EpiAddS e{out, _mm256_set1_ps(s)};
  dispatch_pcb<PFN_DEFAULT>(m, act, e);
}
void qgemv_pcb_i32(const QPackedCB& m, const uint8_t* act, int32_t* out) {  // test/debug only
  EpiI32 e{out};
  dispatch_pcb<PFN_DEFAULT>(m, act, e);
}
int qgemv_pcb_relu2q(const QPackedCB& m, const uint8_t* act, float s_next, uint8_t* q_out, uint16_t* idx_out) {
  if (m.d_in != 192) die("relu2q epilogue requires d_in==192");
  if (m.rows_padded > 768) die("relu2q epilogue requires d_out<=768");
  alignas(64) float y[768];
  EpiF32 e{y};
  run_pcb<3, PFN_DEFAULT>(m, act, e);
  return relu2q_phase2(m.ngroups, m.rows_padded, y, s_next, q_out, idx_out);
}
void qgemv_pcb_quant_bias(const QPackedCB& m, const uint8_t* act, float s_next, uint8_t* q_out) {
  if (m.d_in != 192) die("quant_bias epilogue requires d_in==192");
  if (m.rows_padded > 768) die("quant_bias epilogue requires d_out<=768");
  alignas(64) float y[768];
  EpiF32 e{y};
  run_pcb<3, PFN_DEFAULT>(m, act, e);
  quant_bias_phase2(m.ngroups, m.rows_padded, y, s_next, q_out);
}
int qgemv_pcb_relu2q_dyn(const QPackedCB& m, const uint8_t* act, float s_in, uint8_t* q_out, uint16_t* idx_out,
                         float* s_next) {
  if (m.d_in != 192) die("relu2q_dyn epilogue requires d_in==192");
  if (m.rows_padded > 768) die("relu2q_dyn epilogue requires d_out<=768");
  alignas(64) float h[768];
  EpiRelu2S e{h, _mm256_set1_ps(s_in), _mm256_setzero_ps()};
  run_pcb<3, PFN_DEFAULT>(m, act, e);
  const float s_h = dyn_scale_from_amax_(hmax256_(e.vmax));
  *s_next = s_h;
  return relu2_pack_idx(m.ngroups, m.rows_padded, h, s_h, q_out, idx_out);
}
float qgemv_pcb_quant_bias_dyn(const QPackedCB& m, const uint8_t* act, float s_in, uint8_t* q_out) {
  if (m.d_in != 192) die("quant_bias_dyn epilogue requires d_in==192");
  if (m.rows_padded > 768) die("quant_bias_dyn epilogue requires d_out<=768");
  alignas(64) float y[768];
  EpiF32SAbsMax e{y, _mm256_set1_ps(s_in), _mm256_setzero_ps()};
  run_pcb<3, PFN_DEFAULT>(m, act, e);
  const float s_y = dyn_scale_from_amax_(hmax256_(e.vmax));
  quant_bias_phase2(m.ngroups, m.rows_padded, y, s_y, q_out);
  return s_y;
}

}  // namespace avx512
}  // namespace opt
}  // namespace fx2
