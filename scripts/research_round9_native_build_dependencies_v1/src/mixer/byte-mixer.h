#ifndef BYTE_MIXER_H
#define BYTE_MIXER_H

#include <vector>
#include <memory>

#include "../models/byte-model.h"
#include "lstm.h"

// lext_big knob LEXT_LSTM (compile-time, -DLEXT_LSTM=<mode>; unset/0 =
// cmix-lex-transformer unchanged): runs an online lstm byte mixer alongside
// the pretrained-transformer byte mixer. Mode 1 feeds the lstm the ppmd's
// distribution (as cmix-lex fed its lstm), mode 2 the transformer's output
// distribution, mode 3 both concatenated. See Predictor::LstmMixerByteUpdate.
#ifndef LEXT_LSTM
#define LEXT_LSTM 0
#endif
#if LEXT_LSTM < 0 || LEXT_LSTM > 3
#error "LEXT_LSTM must be unset/0 (off), 1 (ppmd input), 2 (transformer input) or 3 (both)"
#endif

class ByteMixer : public ByteModel {
 public:
  ByteMixer(unsigned int num_models, const unsigned int& bit_context,
      const std::vector<bool>& vocab, unsigned int vocab_size, Lstm* lstm);
  void SetInput(int index, float val);
  void ByteUpdate();
  // Sets the byte-level probability distribution directly (one float per
  // vocabulary byte, in vocabulary order) instead of running the lstm.
  void SetProbs(const float* vocab_probs);

 private:
  std::unique_ptr<Lstm> lstm_;
  const unsigned int& byte_;
  std::valarray<int> byte_map_;
  std::valarray<float> inputs_;
  unsigned int num_models_, vocab_size_, offset_;
};

#if LEXT_LSTM
// The online lstm byte mixer of LEXT_LSTM. This is ByteMixer's lstm path
// (num_models = 1) generalized to an input vector made of num_inputs
// concatenated byte distributions: inputs_ holds num_inputs * vocab_size
// floats, block b (vocabulary order) is filled between two ByteUpdate()
// calls with SetInput(b, byte, p) over the 256 byte values (bytes outside the
// vocabulary are ignored, exactly like ByteMixer::SetInput skips them), and
// ByteUpdate() scales the vector by 2 (ByteMixer's 2 / num_models_ with one
// model), hands it to the lstm together with the completed byte and takes the
// lstm's output distribution over the next byte, like ByteMixer::ByteUpdate.
// The lstm is Lstm(num_inputs * vocab_size, vocab_size, 170, 1, 128, 0.03, 10)
// -- cmix-lex's cell count, horizon, learning rate and gradient clip.
// With num_inputs == 1 the class is ByteMixer(1, ..., new Lstm(...)) exactly.
class LstmByteMixer : public ByteModel {
 public:
  LstmByteMixer(const unsigned int& bit_context,
      const std::vector<bool>& vocab, unsigned int vocab_size,
      unsigned int num_inputs);
  // Sets the probability of byte value `byte` in input block `block`
  // (0 <= block < num_inputs). Bytes outside the vocabulary are ignored.
  void SetInput(unsigned int block, int byte, float val);
  // Feeds the accumulated input vector and the completed byte (bit_context)
  // to the lstm; the lstm's output becomes this model's byte distribution.
  void ByteUpdate();

 private:
  std::unique_ptr<Lstm> lstm_;
  const unsigned int& byte_;
  std::valarray<int> byte_map_;
  std::valarray<float> inputs_;
  unsigned int vocab_size_, num_inputs_;
};
#endif  // LEXT_LSTM

#endif
