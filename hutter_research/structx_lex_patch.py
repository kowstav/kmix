"""Apply the P4 structural-expert integration to an extracted R14 native tree (cwd or argv[1]).

Port of round-6 sxpatch.py to the lexical predictor. Every insertion is guarded by
`#if HP_R14_STRUCTX`, so HP_R14_STRUCTX=0 compiles the original predictor. With 1, the
topology-matched neutral control gets one extra layer-0 input fixed at 0.5 and one extra
layer-0 mixer whose context stays 0; no expert object exists. With 2/3, the expert input
and mixer context come from structx_lex::Expert, keyed by
(kind*4 + confidence)*8 + bit position. The expert updates once per completed byte,
after all bits are coded. Lab only: LAB_IW_OWNERS / LAB_IW_BLOCK0 supply the owner list
that the causal parser built over the preceding stream (regional runs).
"""
import shutil
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
here = Path(__file__).resolve().parent


def patch(path, old, new, count=1):
    s = path.read_text(encoding='utf-8')
    n = s.count(old)
    assert n == count, f'{path}: anchor found {n} times, expected {count}:\n{old}'
    path.write_text(s.replace(old, new), encoding='utf-8', newline='\n')


(root / 'src/hp_r14').mkdir(exist_ok=True)
shutil.copyfile(here / 'structx_lex.h', root / 'src/hp_r14/structx_lex.h')
H, P = root / 'src/predictor.h', root / 'src/predictor.cpp'
patch(H, '#include "hp_r13/native_final_head.h"\n',
      '#include "hp_r13/native_final_head.h"\n#ifndef HP_R14_STRUCTX\n#define HP_R14_STRUCTX 0\n#endif\n'
      '#if HP_R14_STRUCTX\n#include "hp_r14/structx_lex.h"\n#endif\n')
patch(H, '  std::optional<FXCM> fxcm_model_;\n',
      '  std::optional<FXCM> fxcm_model_;\n#if HP_R14_STRUCTX\n  std::optional<structx_lex::Expert> sx_;\n'
      '  unsigned long long sx_ctx_ = 0;\n#endif\n')
patch(P, '  fxcm_stretched_inputs_[4095] = fxcm_neutral_input_;\n', '''  fxcm_stretched_inputs_[4095] = fxcm_neutral_input_;
#if HP_R14_STRUCTX >= 2
  sx_.emplace(vocab_);
  if (const char* owners_path = std::getenv("LAB_IW_OWNERS")) {  // lab only, regional runs
    FILE* f = std::fopen(owners_path, "rb");
    if (!f) Fail("LAB_IW_OWNERS unreadable");
    std::vector<std::string> owners;
    uint32_t n;
    while (std::fread(&n, 4, 1, f) == 1) {
      std::string s(n, '\\0');
      if (n && std::fread(&s[0], 1, n, f) != n) Fail("LAB_IW_OWNERS truncated");
      owners.push_back(s);
    }
    std::fclose(f);
    const char* b0 = std::getenv("LAB_IW_BLOCK0");
    sx_->SetOwners(owners, b0 ? std::strtoull(b0, nullptr, 10) : 0);
  }
#endif
''')
patch(P, '''#if LEXT_TF_APM & 2
  num += 1;  // LEXT_TF_APM mode 2: the APM-refined transformer prediction
#endif
  return num;''', '''#if LEXT_TF_APM & 2
  num += 1;  // LEXT_TF_APM mode 2: the APM-refined transformer prediction
#endif
#if HP_R14_STRUCTX
  num += 1;  // P4 structural expert (neutral 0.5 when inactive)
#endif
  return num;''')
patch(P, '  if (CMIX_L0_MIXER_MASK & (1u << 22)) AddMixer(0, manager_.mx15, 0.005);  // mixer 22\n',
      '  if (CMIX_L0_MIXER_MASK & (1u << 22)) AddMixer(0, manager_.mx15, 0.005);  // mixer 22\n'
      '#if HP_R14_STRUCTX\n  AddMixer(0, sx_ctx_, 0.002);  // P4: selected by expert kind x confidence x bit position\n#endif\n')
patch(P, '''#if LEXT_TF_APM
  tf_apm_predicted_ = true;
#endif
''', '''#if LEXT_TF_APM
  tf_apm_predicted_ = true;
#endif
#if HP_R14_STRUCTX
  {
    float sxp = 0.5f;
    sx_ctx_ = 0;
#if HP_R14_STRUCTX >= 2
    if (sx_ && sx_->Active()) {
      sxp = sx_->PredictBit(manager_.bit_context_);
      int nb = 0;
      for (unsigned int pc = manager_.bit_context_; pc > 1; pc >>= 1) ++nb;
      sx_ctx_ = 1 + (unsigned long long)((sx_->Kind() * 4 + sx_->ConfBucket()) * 8 + nb);
    }
#endif
    layers_[0].SetInput(input_index++, sxp);
  }
#endif
''')
patch(P, '''  manager_.UpdateContexts(bit);
  if (byte_update) {
    if (print_transformer_loss_) AccumulateTransformerLoss();''', '''  manager_.UpdateContexts(bit);
  if (byte_update) {
#if HP_R14_STRUCTX >= 2
    if (sx_) sx_->ByteUpdate(static_cast<unsigned char>(manager_.bit_context_));
#endif
    if (print_transformer_loss_) AccumulateTransformerLoss();''')
patch(P, '    if (!hp_stage_file || n != 14) std::abort();\n',
      '    if (!hp_stage_file || n != 14 + (HP_R14_STRUCTX ? 1 : 0)) std::abort();\n')
print('P4 structural-expert patch applied to', root)
