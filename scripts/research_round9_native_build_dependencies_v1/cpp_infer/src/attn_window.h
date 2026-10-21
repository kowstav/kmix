// Sliding attention window W of the vanilla layers (SPEC.md section 3.5).
//
// Build/export parameter: compile with -DATTN_WIN=<W> (default 1024 = the
// shipped 6m-q4-fp32 checkpoint). Every window-derived size — the int8 KV
// rings (opt/attn.h AttnKVT, model.cpp VanState), the score/exp scratch
// buffers, the naive kernel's scores[] and asserts, the var/fixed kernel
// switch — is derived from this one macro, and the loaders (model.cpp,
// opt/arena_build.cpp) refuse a weights file whose config.ints[6] carries a
// different window: the weights must have been trained/exported with the
// same W (pysrc/export_weights.py writes it; FX2_WINDOW on the Python side,
// see work/sota/train/modal_train.py::export --window).
// The optimized kernels scan K in 32-position double blocks, so W must be a
// positive multiple of 32.
//
// Per-layer windows (2026-09-19, -DATTN_WIN_MULTS=<m0,m1,...>): a checkpoint
// trained with work/sota/train/train_lex.py --window-mults 1,1,2 (pysrc/model.py
// TransformerConfig.window_size_multipliers) runs vanilla-attention layer vi
// (0-based index among the vanilla layers in layer order; 12 layers -> layers
// 3, 7, 11) at window ATTN_WIN * mult(vi). The macro lists one multiplier per
// vanilla layer in layer order; a single entry applies to every layer (default
// 1 = the uniform window of every checkpoint before 2026-09-19). Multipliers
// are small positive integers (<= MAX_MULT); the KV rings / kernels are
// instantiated once per distinct window of the build (opt/attn.cpp), the
// weights file carries the multipliers in config.window_mults (int32, one per
// vanilla layer; absent = all 1; FX2_WINDOW_MULTS on the Python side, see
// modal_train.py::export --window-mults) and the loaders refuse a mismatch
// with this build. RoPE is indexed by the absolute position (tables cover
// 131072 positions), so it is independent of the window.
#pragma once

#include "opt/tf_arch.h"  // TF_NL -> number of vanilla-attention layers (arch::NV)

#ifndef ATTN_WIN
#define ATTN_WIN 1024
#endif

#ifndef ATTN_WIN_MULTS
#define ATTN_WIN_MULTS 1
#endif

static_assert(ATTN_WIN >= 32 && ATTN_WIN % 32 == 0,
              "ATTN_WIN (sliding attention window) must be a positive multiple of 32");

namespace fx2 {
namespace attn_win {

constexpr int NV = opt::arch::NV;  // vanilla-attention layers of this build (tf_arch.h)
constexpr int MAX_MULT = 8;        // largest supported multiplier (kernel dispatch in opt/attn.cpp)
constexpr int MULTS_RAW[] = {ATTN_WIN_MULTS};
constexpr int N_MULTS = static_cast<int>(sizeof(MULTS_RAW) / sizeof(MULTS_RAW[0]));
static_assert(N_MULTS == 1 || N_MULTS == NV,
              "ATTN_WIN_MULTS: one multiplier per vanilla-attention layer (in layer order), or a single one for all");

// window multiplier / window of vanilla layer vi (0 <= vi < NV)
constexpr int mult(int vi) { return N_MULTS == 1 ? MULTS_RAW[0] : MULTS_RAW[vi]; }
constexpr int win(int vi) { return ATTN_WIN * mult(vi); }

constexpr bool mults_valid() {
  for (int vi = 0; vi < NV; vi++)
    if (mult(vi) < 1 || mult(vi) > MAX_MULT) return false;
  return true;
}
static_assert(mults_valid(), "ATTN_WIN_MULTS entries must be in [1, MAX_MULT]");

// does any layer of this build use multiplier m? (the kernels are instantiated for exactly these)
constexpr bool uses_mult(int m) {
  for (int vi = 0; vi < NV; vi++)
    if (mult(vi) == m) return true;
  return false;
}

constexpr int max_win() {
  int w = 0;
  for (int vi = 0; vi < NV; vi++)
    if (win(vi) > w) w = win(vi);
  return w;
}
constexpr int WMAX = max_win();       // largest per-layer window (sizes the shared scratch / naive rings)
constexpr bool UNIFORM = !uses_mult(2) && !uses_mult(3) && !uses_mult(4) && !uses_mult(5) &&
                         !uses_mult(6) && !uses_mult(7) && !uses_mult(8);  // every layer at ATTN_WIN

}  // namespace attn_win
}  // namespace fx2
