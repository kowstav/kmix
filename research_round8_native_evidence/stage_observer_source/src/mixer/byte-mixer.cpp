#include "byte-mixer.h"

ByteMixer::ByteMixer(unsigned int num_models, const unsigned int& bit_context,
    const std::vector<bool>& vocab, unsigned int vocab_size, Lstm* lstm) :
    ByteModel(vocab), lstm_(lstm), byte_(bit_context), byte_map_(0, 256),
    inputs_(0.0, vocab_size), num_models_(num_models), vocab_size_(vocab_size),
    offset_(0) {
  for (int i = 0; i < 256; ++i) {
    byte_map_[i] = offset_;
    if (vocab_[i]) ++offset_;
  }
  offset_ = 0;
}

void ByteMixer::SetInput(int index, float val) {
  if (!vocab_[index]) return;
  inputs_[offset_] += val;
  ++offset_;
  if (offset_ == vocab_size_) offset_ = 0;
}

void ByteMixer::SetProbs(const float* vocab_probs) {
  unsigned int k = 0;
  for (int i = 0; i < 256; ++i) {
    if (vocab_[i]) {
      probs_[i] = vocab_probs[k];
      ++k;
    } else {
      probs_[i] = 0;
    }
  }
  ByteModel::ByteUpdate();
}

void ByteMixer::ByteUpdate() {
  inputs_ *= 2 / num_models_;
  lstm_->SetInput(inputs_);
  inputs_ = 0;
  const auto& output = lstm_->Perceive(byte_map_[byte_]);
  offset_ = 0;
  for (int i = 0; i < 256; ++i) {
    if (vocab_[i]) {
      probs_[i] = output[offset_];
      ++offset_;
    } else {
      probs_[i] = 0;
    }
  }
  offset_ = 0;
  ByteModel::ByteUpdate();
}

#if LEXT_LSTM
LstmByteMixer::LstmByteMixer(const unsigned int& bit_context,
    const std::vector<bool>& vocab, unsigned int vocab_size,
    unsigned int num_inputs) : ByteModel(vocab),
    lstm_(new Lstm(num_inputs * vocab_size, vocab_size, 170, 1, 128, 0.03,
        10)),
    byte_(bit_context), byte_map_(0, 256),
    inputs_(0.0, num_inputs * vocab_size), vocab_size_(vocab_size),
    num_inputs_(num_inputs) {
  unsigned int k = 0;
  for (int i = 0; i < 256; ++i) {
    byte_map_[i] = k;
    if (vocab_[i]) ++k;
  }
}

void LstmByteMixer::SetInput(unsigned int block, int byte, float val) {
  if (!vocab_[byte]) return;
  inputs_[block * vocab_size_ + byte_map_[byte]] = val;
}

void LstmByteMixer::ByteUpdate() {
  inputs_ *= 2.0f;  // ByteMixer::ByteUpdate's `inputs_ *= 2 / num_models_`
  lstm_->SetInput(inputs_);
  inputs_ = 0;
  const std::valarray<float>& output = lstm_->Perceive(byte_map_[byte_]);
  unsigned int k = 0;
  for (int i = 0; i < 256; ++i) {
    if (vocab_[i]) {
      probs_[i] = output[k];
      ++k;
    } else {
      probs_[i] = 0;
    }
  }
  ByteModel::ByteUpdate();
}
#endif  // LEXT_LSTM
