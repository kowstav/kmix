// qmat.h — quantized-matmul weight-arena format + descriptors (AVX2 / Zen 2).
//
// This file DEFINES the weight storage format the optimized kernels consume.
// At integration this becomes the model's in-memory format (the weights FILE
// stays as in SPEC section 4; the loader repacks into these arenas).
//
// =========================================================================
// 1. DENSE ROW-MAJOR ARENA (one per matmul, consumed strictly sequentially)
// =========================================================================
// Weights are UNPACKED int8 (one byte per weight, values in [-7,7], two's
// complement). Per MACHINE.md section 3 this beats packed int4 at the model's
// ~6 MB L3 footprint (20.4-21.4 vs 18.6-20.4 MAC/cyc).
//
// Geometry:
//   stride      = round_up(d_in, 32)          (in-dim padded, pad weights = 0)
//   group_rows  = 8  if d_in <= 256           (G8 kernels)
//                 4  if d_in == 768           (G4 kernel, register pressure)
//   rows_padded = round_up(d_out, group_rows) (pad rows: weights 0, scale 0,
//                                              corr 0 -> output rows = +0.0f)
//   nchunk      = stride / 32
//   ngroups     = rows_padded / group_rows
//
// Arena = ngroups consecutive GROUP BLOCKS, base 64B-aligned, no gaps:
//   group block (G8) = [ 8 x int32 corr | 8 x fp32 scale |  weights ]
//                          32 B              32 B          nchunk*8*32 B
//   group block (G4) = [ 4 x int32 corr | 4 x fp32 scale |  weights ]
//                          16 B              16 B          nchunk*4*32 B
//   weights are chunk-major: for c in [0,nchunk): for r in [0,group_rows):
//     the 32 bytes of row (group*group_rows + r), columns [32c, 32c+32).
//
// Metadata semantics (per row o):
//   scale[o] = fold = s_act * fp32(bf16(w_scale[o]))   (can be NEGATIVE)
//   corr[o]  = 128 * sum_i qw[o][i]   if the activation is BIASED u8
//                                     (qa + 128, qa in [-128,127])
//            = 0                      if the activation is RAW u8 in [0,127]
//                                     (relu^2 outputs, quantized priors)
// The kernel computes  dot[o] = sum_i act_u8[i]*qw[o][i] - corr[o]  which for
// the biased case equals the exact signed int32 dot sum_i qa[i]*qw[o][i]
// (16-bit intermediate accumulation is safe: <= 8 chunk maddubs results,
// 8*2*255*7 = 28560 < 32767). The bias convention is thus a property of the
// ARENA, not of the kernel.
//
// Group bytes: d_in=192: 1600, d_in=64: 576, d_in=224(prior): 1856 (all
// multiples of 64); d_in=768: 3104 (multiple of 32).
//
// The buffer holding an arena must have QMAT_TAIL_SLACK extra mapped bytes
// after the stream (software prefetch runs ~2 KB ahead).
//
// Activation vectors passed to the kernels must be 32B-aligned and padded
// with zeros to `stride` bytes (padding value is irrelevant for correctness
// when pad weights are 0, but 0 keeps sums reproducible).
//
// Output buffers must have room for `rows_padded` floats (only the unembedding
// 205->208 actually pads; pad entries are written/clobbered).
//
// =========================================================================
// 2. SPARSE COLUMN-MAJOR ARENA (192-out matmuls with sparse RAW-u8 inputs:
//    mlp.down 192x768, prior_embedding 192x205)
// =========================================================================
//   cols   : d_in consecutive columns; column c = 192 int8 (rows in natural
//            order, values [-7,7]) at byte offset c*192. Base 64B-aligned ->
//            every column is 64B-aligned (192 = 3 cache lines).
//   fold   : separate 64B-aligned fp32[192] of per-row folded scales.
// Input activations are RAW u8 in [0,127] (relu^2 / prior ints; zero skipping
// is exact because a q==0 column contributes nothing). The caller supplies the
// dense u8 vector plus a u16 index list of the nonzero positions (produced for
// free by the mlp.up relu^2 epilogue). corr is always 0 here.
// The index buffer must have >= 8 writable slack entries past nnz (the
// producers write in 16 B blocks; slack entries hold in-range values, which
// keeps the kernel's lookahead prefetch on mapped memory).
//
// =========================================================================
// 3. PACKED INT4 ARENA (compile-time ALTERNATIVE, for the packed-vs-unpacked
//    comparison; not the recommended production format)
// =========================================================================
// 4-row groups: [4 x fp32 scale, 16 B pad | nibbles]. Per 32-byte weight
// vector: row r columns [64p,64p+32) in the LOW nibbles and [64p+32,64p+64)
// in the HIGH nibbles, stored as unsigned qw+7 in [0,14]. Activations SIGNED
// int8 (unbiased; raw [0,127] values also work). The correction is the single
// scalar 7*sum_i qa[i], passed by the caller. stride4 = round_up(d_in, 64).
//
// =========================================================================
// 4. PACKED INT4 + LUT ARENA (QPackedCB, 2026-09-19; the dense format of the
//    AVX-512 fast path, -DTF_AVX512=1)
// =========================================================================
// 8-row groups [8 x int32 corr | 8 x fp32 scale | npair x (8 rows x 32 B of
// nibbles)] = 64 + 256*npair bytes (64B-aligned blocks), stride4 =
// round_up(d_in, 64), npair = stride4 / 64, rows_padded = round_up(d_out, 8).
// Row r, pair p, byte j: LOW nibble = column 64p+j, HIGH nibble = column
// 64p+32+j. A nibble holds the LEVEL INDEX q+7 in [0,14] (plain int4: the
// value + 7; QMAT_CODEBOOK: the codebook index) and the kernel maps it to the
// signed int8 weight through a 16-entry LUT (vpshufb; entry 15 = 0, the pad
// value of pad rows / pad columns), so one format serves both weight kinds.
// Activations, corr and the folded row scales follow the QDense conventions
// (section 1) exactly, hence the same fp32 epilogues and outputs bit-identical
// to the QDense kernels on the same logical weights (test_avx512). Half the
// bytes of the unpacked arena: the per-token weight stream drops from ~7.2 MB
// to ~4.4 MB on AVX-512 hosts. Consumed ONLY by the qmat_avx512.h kernels
// (nibble unpack + LUT are free under vpdpbusd, not under vpmaddubsw).
//
// =========================================================================
// All builders take the same inputs the model loader has: row-major int8
// weights in [-7,7] and the folded per-row fp32 scales.
#pragma once

#include <cstddef>
#include <cstdint>

namespace fx2 {
namespace opt {

// mapped slack required after every arena (prefetch overrun)
constexpr size_t QMAT_TAIL_SLACK = 4096;

// TF_AVX512 (2026-09-19, -DTF_AVX512=1; lext_big knob TF_AVX512=1): compile the AVX-512 VNNI fast path
// (qmat_avx512.h, qmat_dense_avx512.cpp, qmat_sparse_avx512.cpp) and select it at RUN TIME on CPUs with
// AVX-512 F/BW/VL/VNNI (qmat_cpu.h cpu_has_avx512_vnni(): Tiger Lake, Ice Lake, Sapphire Rapids, Zen 4 ...).
// The AVX2 kernels stay the default (Zen 2 and older) and both paths produce BIT-IDENTICAL outputs -- an
// archive compressed on one path decodes on the other. Default 0 = the AVX2-only build, unchanged.
#ifndef TF_AVX512
#define TF_AVX512 0
#endif

// =========================================================================
// CODEBOOK WEIGHTS (2026-09-18, -DQMAT_CODEBOOK=1 -DQMAT_WMAX=<max|value|>)
// =========================================================================
// pysrc/export_weights.py with FX2_WCODEBOOK=1 stores every quantized matrix
// as the LEVEL INDEX (<name>.weight.q, int8 in [-7,7] like plain int4) plus a
// 15-entry integer codebook <name>.weight.codebook (int8, |value| <= QMAT_WMAX,
// units of CODEBOOK_GRID row scales): weight = scale * grid * codebook[q + 7].
// The loaders map indices to codebook values while building the DENSE arenas
// (unpacked int8, values in [-QMAT_WMAX, QMAT_WMAX]) and fold `grid` into the
// per-row scales, so the dense kernels are unchanged except for the int16
// accumulation depth; the nibble-packed sparse arenas keep the index (0..14)
// and the kernel maps it through a per-matrix 16-byte LUT (vpshufb).
#ifndef QMAT_CODEBOOK
#define QMAT_CODEBOOK 0
#endif
#ifndef QMAT_WMAX
#define QMAT_WMAX (QMAT_CODEBOOK ? 21 : 7)
#endif
static_assert(QMAT_WMAX >= 7 && QMAT_WMAX <= 63, "QMAT_WMAX out of range");
// exact int16 accumulation depth of vpmaddubsw partial sums (no saturation):
//   dense kernels, biased u8 activations (<= 255), 32-column chunks:
constexpr int QMAT_WIDEN_CHUNKS = 32767 / (2 * 255 * QMAT_WMAX);   // 9 (int4) -> 8 chunks stay exact; 3 for |w| <= 21
//   sparse column kernels, raw u8 activations (<= 127), column pairs:
constexpr int QMAT_FLUSH_PAIRS = 32767 / (2 * 127 * QMAT_WMAX);    // 18 (int4), 6 for |w| <= 21
static_assert(QMAT_WIDEN_CHUNKS >= 1 && QMAT_FLUSH_PAIRS >= 1, "QMAT_WMAX too large");

// =========================================================================
// 8-BIT SMALL MATMULS (2026-09-18, -DQMAT_SMALL_W8=1): the token embedding,
// the prior embedding (192x205, raw u8 acts) and the unembedding (205x192,
// biased u8 acts) carry int8 weights in [-127,127] (pysrc/export_weights.py
// with FX2_WBITS_SMALL=8; PTQ sensitivity: the prior projection alone is 43 %
// of the int4 penalty). vpmaddubsw cannot hold 255*127*2, so these two
// matmuls use an int16-widened vpmaddwd kernel (exact int32; ~40 K MACs per
// token each, negligible). Weights row-major, stride = round_up(d_in, 32).
// =========================================================================
#ifndef QMAT_SMALL_W8
#define QMAT_SMALL_W8 0
#endif
struct QW8 {
  const int8_t* w = nullptr;      // [rows_padded][stride], pad rows/cols 0
  const int32_t* corr = nullptr;  // 128 * sum_i w[o][i] for biased acts, else 0
  const float* fold = nullptr;    // s_act * w_scale[o]
  int d_out = 0, d_in = 0, stride = 0, rows_padded = 0;
};
size_t qw8_bytes(int d_out, int d_in);   // weight bytes (rows_padded * stride)
// dst_w 64B-aligned (qw8_bytes), dst_corr / dst_fold: rows_padded entries each.
QW8 qw8_build(int8_t* dst_w, int32_t* dst_corr, float* dst_fold, const int8_t* qw, const float* fold,
              int d_out, int d_in, bool biased_input);
// out[o] = fold[o] * float(sum_i act[i]*w[o][i] - corr[o]) for o < rows_padded (pad rows -> 0.0f);
// act: u8, zero-padded to stride.
void qw8_f32(const QW8& m, const uint8_t* act, float* out);

constexpr int qmat_round_up(int x, int m) { return (x + m - 1) / m * m; }

constexpr int qmat_group_rows(int d_in) { return d_in <= 256 ? 8 : 4; }

// ---------------- dense row-major descriptor ----------------
struct QDense {
  const uint8_t* arena = nullptr;  // 64B-aligned group-block stream
  int d_out = 0, d_in = 0;
  int stride = 0;       // round_up(d_in, 32)
  int nchunk = 0;       // stride / 32
  int group_rows = 0;   // 8 or 4
  int ngroups = 0;      // rows_padded / group_rows
  int rows_padded = 0;  // round_up(d_out, group_rows)
  size_t bytes = 0;     // total stream bytes (multiple of the group size)
};

// arena size in bytes (excluding QMAT_TAIL_SLACK)
size_t qdense_bytes(int d_out, int d_in);

// Build a dense arena into dst (64B-aligned, qdense_bytes + QMAT_TAIL_SLACK
// mapped). qw is row-major [d_out][d_in] in [-7,7]; fold[d_out] the folded
// fp32 row scales. biased_input selects the corr convention (see above).
QDense qdense_build(uint8_t* dst, const int8_t* qw, const float* fold,
                    int d_out, int d_in, bool biased_input);

// ---------------- sparse column-major descriptor ----------------
struct QSparse {
  const int8_t* cols = nullptr;  // 64B-aligned, d_in * 192 bytes
  const float* fold = nullptr;   // 64B-aligned fp32[192]
  int d_in = 0;
  int d_out = 0;  // always 192
};

size_t qsparse_bytes(int d_in);  // = d_in * 192

// dst_cols 64B-aligned with qsparse_bytes + QMAT_TAIL_SLACK mapped;
// dst_fold 64B-aligned fp32[192]. d_out must be 192.
QSparse qsparse_build(int8_t* dst_cols, float* dst_fold, const int8_t* qw,
                      const float* fold, int d_out, int d_in);

// ---- int4-packed column variant (RECOMMENDED for the sparse matmuls) ----
// The index-driven gather is cache-LINE-fetch-bound under realistic full-
// stream conditions (measured ~17-22 cyc/col for 3-line int8 columns), so
// halving the column to 2 lines wins ~20-30% despite extra unpack ALU:
//   column c at byte offset c*128: 96 bytes of nibbles (byte b: LOW nibble =
//   row b + 7, HIGH nibble = row 96+b + 7, values [0,14]) + 32 pad bytes.
//   Base 64B-aligned -> every column is exactly 2 aligned cache lines.
// The kernel keeps the nibbles unsigned as the vpmaddubsw unsigned operand
// (activation pair as the signed one) and subtracts the exact global
// correction 7 * sum(processed act values) once in the int32 epilogue:
// results are bit-identical to the int8 column kernels. The one-sided s16
// bound (2*14*127 = 3556 per pair) means it widens every 9 pairs.
struct QSparse4 {
  const uint8_t* cols = nullptr;  // 64B-aligned, d_in * 128 bytes
  const float* fold = nullptr;    // 64B-aligned fp32[192]
  int d_in = 0;
  int d_out = 0;  // always 192
  // QMAT_CODEBOOK: nibble n (= level index, 0..14) -> signed int8 codebook value; entry 15 = 0 (pad).
  // Both 16-byte lanes hold the same table (vpshufb works per 128-bit lane).
  alignas(32) int8_t lut[32] = {0};
};

size_t qsparse4_bytes(int d_in);  // = d_in * 128
QSparse4 qsparse4_build(uint8_t* dst_cols, float* dst_fold, const int8_t* qw,
                        const float* fold, int d_out, int d_in);

// ---------------- packed int4 descriptor (comparison alternative) ---------
struct QPacked {
  const uint8_t* arena = nullptr;
  int d_out = 0, d_in = 0;
  int stride4 = 0;  // round_up(d_in, 64): logical cols per row
  int npair = 0;    // stride4 / 64: 32-byte weight vectors per row
  int ngroups = 0;  // rows_padded4 / 4
  int rows_padded = 0;
  size_t bytes = 0;
};

size_t qpacked_bytes(int d_out, int d_in);
QPacked qpacked_build(uint8_t* dst, const int8_t* qw, const float* fold,
                      int d_out, int d_in);

// ---------------- packed int4 + LUT descriptor (section 4; AVX-512 path) ----
struct QPackedCB {
  const uint8_t* arena = nullptr;  // 64B-aligned group-block stream
  int d_out = 0, d_in = 0;
  int stride4 = 0;      // round_up(d_in, 64)
  int npair = 0;        // stride4 / 64
  int ngroups = 0;      // rows_padded / 8
  int rows_padded = 0;  // round_up(d_out, 8)
  size_t bytes = 0;     // ngroups * (64 + 256 * npair)
  // nibble (level index 0..14) -> signed int8 weight; entry 15 = 0 (pad). The 16-byte table is replicated in all
  // four 128-bit lanes (vpshufb works per lane).
  alignas(64) int8_t lut[64] = {0};
};

// arena size in bytes (excluding QMAT_TAIL_SLACK)
size_t qpackedcb_bytes(int d_out, int d_in);
// Build a packed+LUT arena into dst (64B-aligned, qpackedcb_bytes + QMAT_TAIL_SLACK mapped). q is row-major
// [d_out][d_in] of LEVEL INDICES in [-7,7] (plain int4: the weight values themselves); codebook15 = the 15 signed
// level values (index q+7 -> weight, |v| <= QMAT_WMAX) or nullptr for the identity (weight = q); fold[d_out] the
// folded fp32 row scales (grid included for codebook weights); biased_input selects the corr convention
// (section 1). Baseline (AVX2) code: the loader builds it on AVX-512 hosts only.
QPackedCB qpackedcb_build(uint8_t* dst, const int8_t* q, const int8_t* codebook15, const float* fold, int d_out,
                          int d_in, bool biased_input);

// Empirically determined density threshold (bench_qmat): above this nonzero
// fraction, switch from the index-driven sparse kernel to the column-dense
// fallback. Measured on the int4 column arenas the two are within noise of
// each other even at density 1.0 (the index-driven loop is the same pair
// loop and becomes sequential), so the fallback exists only to bound the
// worst case; with a row-major dense arena also resident one could switch to
// qgemv_add at ~0.65 instead (7.0 vs ~8.5 Kcyc at density 1), at +1.7 MB L3.
constexpr float QMAT_SPARSE_DENSITY_THRESHOLD = 0.95f;

}  // namespace opt
}  // namespace fx2
