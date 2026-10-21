# Integrate structx::Expert (decoder-causal structural experts for the PHDA9 tail) into the
# cmix predictor of the fx2-cmix-transformer tree (cwd). One extra mixer input + one extra
# layer-0 mixer selected by (expert kind, confidence, bit position). LAB_SX=0 keeps the exact
# same topology with a neutral input (clean A/B). Lab-only: LAB_IW_OWNERS / LAB_IW_BLOCK0.
import shutil
def patch(path, old, new, count=1):
    s = open(path, encoding='utf-8').read()
    n = s.count(old)
    assert n == count, f'{path}: anchor found {n} times, expected {count}:\n{old}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new))

shutil.copy('/root/hp/tools/structx.h', 'src/structx.h')
P, H = 'src/predictor.cpp', 'src/predictor.h'
patch(H, '#include "../cpp_infer/src/opt/model_opt.h"', '#include "../cpp_infer/src/opt/model_opt.h"\n#include "structx.h"')
patch(H, '  std::optional<FXCM> fxcm_model_;',
      '  std::optional<FXCM> fxcm_model_;\n  std::optional<structx::Expert> sx_;\n  unsigned long long sx_ctx_ = 0;')
patch(P, '''  fxcm_model_.emplace();''', '''  fxcm_model_.emplace();
  if (vocab_size_ == 205 && !(getenv("LAB_SX") && atoi(getenv("LAB_SX")) == 0)) {
    sx_.emplace(vocab_);
    std::string sep;
    for (unsigned char idx : kArticleSeparator) sep.push_back((char)vocab_bytes_[idx]);
    const size_t l = sep.rfind('L');
    std::string title_end = "L/" + sep.substr(l + 1, sep.size() - l - 2) + "N";
    sx_->SetPatterns(sep, title_end);
    if (getenv("LAB_IW_OWNERS")) {  // lab only: owners as the stream parser would produce
      FILE* f = fopen(getenv("LAB_IW_OWNERS"), "rb");
      if (!f) Fail("LAB_IW_OWNERS unreadable");
      std::vector<std::string> owners;
      uint32_t n;
      while (fread(&n, 4, 1, f) == 1) {
        std::string s(n, '\\0');
        if (n && fread(&s[0], 1, n, f) != n) Fail("LAB_IW_OWNERS truncated");
        owners.push_back(s);
      }
      fclose(f);
      sx_->SetOwners(owners, getenv("LAB_IW_BLOCK0") ? strtoull(getenv("LAB_IW_BLOCK0"), nullptr, 10) : 0);
    }
  }''')
patch(P, '''  num += byte_mixer_->NumOutputs();
  return num;''', '''  num += byte_mixer_->NumOutputs();
  num += 1;  // structural expert (neutral when inactive)
  return num;''')
patch(P, '''  AddMixer(0, manager_.mx15, 0.005);
''', '''  AddMixer(0, manager_.mx15, 0.005);
  AddMixer(0, sx_ctx_, 0.002);
''')
patch(P, '''  auto byte_mixer_index = input_index - 1;
''', '''  auto byte_mixer_index = input_index - 1;
  {
    float sxp = 0.5f;
    sx_ctx_ = 0;
    if (sx_ && sx_->Active()) {
      sxp = sx_->PredictBit(manager_.bit_context_);
      int nb = 0;
      for (unsigned int pc = manager_.bit_context_; pc > 1; pc >>= 1) ++nb;
      sx_ctx_ = 1 + (unsigned long long)((sx_->Kind() * 4 + sx_->ConfBucket()) * 8 + nb);
    }
    layers_[0].SetInput(input_index++, sxp);
  }
''')
patch(P, '''  manager_.UpdateContexts(bit);
  if (byte_update) {
    if (print_transformer_loss_) AccumulateTransformerLoss();''', '''  manager_.UpdateContexts(bit);
  if (byte_update) {
    if (sx_) sx_->ByteUpdate((unsigned char)manager_.bit_context_);
    if (print_transformer_loss_) AccumulateTransformerLoss();''')
print('structural-expert patch applied')
