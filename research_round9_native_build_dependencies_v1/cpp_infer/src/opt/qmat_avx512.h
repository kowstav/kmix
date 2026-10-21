// qmat_avx512.h -- AVX-512 (F/BW/VL/VNNI) variants of the hot qmat kernels (TF_AVX512 fast path, 2026-09-19).
//
// Same arena formats as qmat.h (the loader builds ONE arena set per site; QDense / QSparse4 / QW8 arenas are
// shared by both paths, the QPackedCB dense arena exists only on AVX-512 hosts), same public contracts as
// qmat_dense.h / qmat_sparse.h, and BIT-IDENTICAL outputs to the AVX2 kernels:
//   * every int32 dot is an exact integer: vpdpbusd accumulates u8*s8 groups of 4 straight into int32
//     (no int16 stage, no saturation; |dot| <= 768*255*127 < 2^31), and the AVX2 path never saturates
//     by construction (QMAT_WIDEN_CHUNKS / QMAT_FLUSH_PAIRS), so any summation order gives the same integer;
//   * the fp32 epilogues apply exactly the AVX2 formulas, op for op (cvtepi32_ps, mul, [mul s], [add];
//     never fused), and the phase-2 quantizers are verbatim copies -> identical floats and bytes.
// Verified by test_avx512 (every entry point vs its AVX2 twin and the scalar int64 reference).
//
// qmat_dense_avx512.cpp / qmat_sparse_avx512.cpp are compiled with the baseline flags PLUS
// -mavx512f -mavx512bw -mavx512vl -mavx512vnni (NOT -march=x86-64-v4: it lacks VNNI) and must only be
// CALLED after cpu_has_avx512_vnni() (qmat_cpu.h) returned true; the AVX2 kernels remain the default path.
// -DQMAT_AVX512_ALL_SHAPES=1 (tests) also compiles the shapes the production model does not dispatch
// (d_in 205/224/768 dense, npair 1/4/12 packed).
#pragma once

#include "qmat.h"

namespace fx2 {
namespace opt {
namespace avx512 {

// ---- dense row-major arenas (qmat_dense.h (a)-(h) + i32 / nopf test variants) ----
void qgemv_f32(const QDense& m, const uint8_t* act, float* out);
void qgemv_add(const QDense& m, const uint8_t* act, float* out);
void qgemv_f32s(const QDense& m, const uint8_t* act, float s, float* out);
void qgemv_adds(const QDense& m, const uint8_t* act, float s, float* out);
int qgemv_relu2q(const QDense& m, const uint8_t* act, float s_next, uint8_t* q_out, uint16_t* idx_out);
void qgemv_quant_bias(const QDense& m, const uint8_t* act, float s_next, uint8_t* q_out);
int qgemv_relu2q_dyn(const QDense& m, const uint8_t* act, float s_in, uint8_t* q_out, uint16_t* idx_out,
                     float* s_next);
float qgemv_quant_bias_dyn(const QDense& m, const uint8_t* act, float s_in, uint8_t* q_out);
void qgemv_i32(const QDense& m, const uint8_t* act, int32_t* out);
void qgemv_f32_nopf(const QDense& m, const uint8_t* act, float* out);

// ---- packed int4 + LUT arena (qmat.h section 4, QPackedCB): same contracts as the QDense kernels ----
void qgemv_pcb_f32(const QPackedCB& m, const uint8_t* act, float* out);
void qgemv_pcb_add(const QPackedCB& m, const uint8_t* act, float* out);
void qgemv_pcb_f32s(const QPackedCB& m, const uint8_t* act, float s, float* out);
void qgemv_pcb_adds(const QPackedCB& m, const uint8_t* act, float s, float* out);
int qgemv_pcb_relu2q(const QPackedCB& m, const uint8_t* act, float s_next, uint8_t* q_out, uint16_t* idx_out);
void qgemv_pcb_quant_bias(const QPackedCB& m, const uint8_t* act, float s_next, uint8_t* q_out);
int qgemv_pcb_relu2q_dyn(const QPackedCB& m, const uint8_t* act, float s_in, uint8_t* q_out, uint16_t* idx_out,
                         float* s_next);
float qgemv_pcb_quant_bias_dyn(const QPackedCB& m, const uint8_t* act, float s_in, uint8_t* q_out);
void qgemv_pcb_i32(const QPackedCB& m, const uint8_t* act, int32_t* out);

// ---- 8-bit small matmuls (qmat.h QW8) ----
void qw8_f32(const QW8& m, const uint8_t* act, float* out);

// ---- int4 column arenas (qmat.h QSparse4; qmat_sparse.h contracts) ----
void qsparse4_f32(const QSparse4& m, const uint8_t* q8, const uint16_t* idx, int nnz, float* out);
void qsparse4_add(const QSparse4& m, const uint8_t* q8, const uint16_t* idx, int nnz, float* out);
void qsparse4_i32(const QSparse4& m, const uint8_t* q8, const uint16_t* idx, int nnz, int32_t* out);
void qsparse4_dense_f32(const QSparse4& m, const uint8_t* q8, float* out);
void qsparse4_dense_add(const QSparse4& m, const uint8_t* q8, float* out);
void qsparse4_dense_i32(const QSparse4& m, const uint8_t* q8, int32_t* out);
void qsparse4_f32s(const QSparse4& m, const uint8_t* q8, const uint16_t* idx, int nnz, float s, float* out);
void qsparse4_adds(const QSparse4& m, const uint8_t* q8, const uint16_t* idx, int nnz, float s, float* out);
void qsparse4_dense_f32s(const QSparse4& m, const uint8_t* q8, float s, float* out);
void qsparse4_dense_adds(const QSparse4& m, const uint8_t* q8, float s, float* out);

}  // namespace avx512
}  // namespace opt
}  // namespace fx2
