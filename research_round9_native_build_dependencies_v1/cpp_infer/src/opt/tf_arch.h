// tf_arch.h -- architecture build parameters of the transformer inference engine (lext_big, 2026-09-09).
// TF_NL   = number of layers (default 12), TF_DMLP = MLP hidden width (default 768). Both must equal the
// exported checkpoint's config.ints[2] / [5] (the loader refuses a mismatch). Vanilla sliding-window attention
// sits on every 4th layer counted from the END (12 -> layers 3,7,11 = the authors' pattern; 10 -> 1,5,9), the
// other layers are Kimi linear attention; skip connections pair source layer s (0 <= s < NL/2) with destination
// NL-1-s, exactly as pysrc/model.py does for any NL.
#pragma once
#ifndef TF_NL
#define TF_NL 12
#endif
// TF_ACTQ_DYN (2026-09-19, -DTF_ACTQ_DYN=1): the checkpoint was trained with train_lex.py --actq-dynamic-mm -- every matmul input
// activation (kimi/vanilla q/k/v + gate projections, out projections, mlp up/down, prior embedding, unembedding) is int8-quantized
// with a PER-TOKEN scale s = max(max_i |x_i|, 1e-12) / 127 computed from the vector itself (pysrc/quantization.py Quantize.forward,
// dynamic branch) instead of a learned static scale; the post-rope q/k/v quantizers of the vanilla attention keep their learned
// static per-head scales (int8 KV ring). The weights file carries config.actq_dynamic_mm = 1 and no .quantize_activation.scale
// tensors; the loaders refuse a file whose flag differs from this build (SPEC.md section 2a).
#ifndef TF_ACTQ_DYN
#define TF_ACTQ_DYN 0
#endif
#ifndef TF_DMLP
#define TF_DMLP 768
#endif
static_assert(TF_NL >= 4 && TF_NL <= 24, "TF_NL");
static_assert(TF_DMLP >= 64 && TF_DMLP <= 768 && TF_DMLP % 64 == 0, "TF_DMLP (relu2q epilogue buffers hold <= 768)");
namespace fx2 { namespace opt { namespace arch {
constexpr int NL = TF_NL, DMLP = TF_DMLP, NSKIP = TF_NL / 2;
constexpr bool kimi_at(int l) { return ((NL - 1 - l) % 4) != 0; }
constexpr int count_kimi() { int n = 0; for (int l = 0; l < NL; l++) n += kimi_at(l) ? 1 : 0; return n; }
constexpr int NK = count_kimi(), NV = NL - NK;
struct KimiPattern { bool v[NL]; };
constexpr KimiPattern kimi_pattern() { KimiPattern p{}; for (int l = 0; l < NL; l++) p.v[l] = kimi_at(l); return p; }
constexpr KimiPattern KIMI = kimi_pattern();
static_assert(NL != 12 || (NK == 9 && NV == 3 && !KIMI.v[3] && !KIMI.v[7] && !KIMI.v[11]), "default pattern");
}}}  // namespace fx2::opt::arch
