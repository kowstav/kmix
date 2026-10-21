#pragma once
#include <cstdint>

// This state is updated only after a real coded bit. No teacher/oracle inputs.
class HPCausalAdaptive {
 public:
  uint32_t Predict(uint32_t native_p, float neural_p, bool previous_valid);
  void Observe(int bit);
 private:
  double weights_[5] = {0.2,0.2,0.2,0.2,0.2};
  uint32_t experts_[5] = {};
  bool pending_ = false;
};
