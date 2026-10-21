# Port cmix-lex's fxcm_v26 text model into the fx2-cmix-transformer tree (cwd).
# Keeps fx2-cmix-T's PPMD (so the transformer's priors are bit-identical) and its transformer
# integration; swaps src/models/fxcmv1.{cpp,h} and feeds fxcm's raw outputs through cmix-lex's
# stretched lookup table exactly as cmix-lex's predictor does.
import shutil
LEX = '/root/hp/src/cmix-lex'

def patch(path, old, new, count=1):
    s = open(path, encoding='utf-8').read()
    n = s.count(old)
    assert n == count, f'{path}: anchor found {n} times, expected {count}:\n{old}'
    s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)

for f in ['src/models/fxcmv1.cpp', 'src/models/fxcmv1.h']:
    s = open(f'{LEX}/{f}', encoding='utf-8', errors='surrogateescape').read().replace('\r\n', '\n')
    open(f, 'w', encoding='utf-8', errors='surrogateescape').write(s)

patch('src/mixer/mixer-input.h', '  void SetStretchedInput(int index, float p);',
      '  void SetStretchedInput(int index, float p);\n  void SetStretchedInputUnchecked(int index, float p) { inputs_[index] = p; }')

patch('src/predictor.h', '#include <vector>\n#include <set>', '#include <vector>\n#include <array>\n#include <set>')
patch('src/predictor.h', '  std::optional<FXCM> fxcm_model_;',
      '  std::optional<FXCM> fxcm_model_;\n  std::array<float, 4096> fxcm_stretched_inputs_;\n  float fxcm_neutral_input_ = 0.0f;')

patch('src/predictor.cpp', '''  fxcm_model_.emplace();
  AddWord();''', '''  fxcm_model_.emplace();
  fxcm_neutral_input_ = sigmoid_.Logit(0.5f);
  for (int raw = -2047; raw <= 2047; ++raw) {
    float p = fxcm_model_->RawPredictionProbability(static_cast<short>(raw));
    if (p < 1.0e-4f) p = 1.0e-4f;
    else if (p > 1.0f - 1.0e-4f) p = 1.0f - 1.0e-4f;
    fxcm_stretched_inputs_[raw + 2047] = sigmoid_.Logit(p);
  }
  fxcm_stretched_inputs_[4095] = fxcm_neutral_input_;
  AddWord();''')

patch('src/predictor.cpp', '''  const auto& fxcm_model_outputs = fxcm_model_->Predict();
  for (unsigned int j = 0; j < fxcm_model_outputs.size(); ++j) {
    layers_[0].SetInput(input_index, fxcm_model_outputs[j]);
    ++input_index;
  }''', '''  const unsigned int fxcm_model_outputs = fxcm_model_->NumOutputs();
  const short* fxcm_raw_outputs = fxcm_model_->RawPredictions();
  unsigned int fxcm_active_outputs = fxcm_model_->ActivePredictions();
  if (fxcm_active_outputs > fxcm_model_outputs) fxcm_active_outputs = fxcm_model_outputs;
  for (unsigned int j = 0; j < fxcm_active_outputs; ++j) {
    layers_[0].SetStretchedInputUnchecked(
        input_index, fxcm_stretched_inputs_[fxcm_raw_outputs[j] + 2047]);
    ++input_index;
  }
  for (unsigned int j = fxcm_active_outputs; j < fxcm_model_outputs; ++j) {
    layers_[0].SetStretchedInputUnchecked(input_index, fxcm_neutral_input_);
    ++input_index;
  }''')
print('fxcm_v26 port applied')
