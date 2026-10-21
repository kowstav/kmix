#include "hp_calibration_odds.h"
#include "encoder.h"
#include <cmath>
#include <cstdio>
#include <cstdlib>
static FILE* hp_final_bit_trace = nullptr;
double g_lab_cost_bits=0;

Encoder::Encoder(std::ofstream* os, Predictor* p) : os_(os), x1_(0),
    x2_(0xffffffff), p_(p) {}

void Encoder::WriteByte(unsigned int byte) {
  out_.push_back(byte);
}

unsigned int Encoder::Discretize(float p) {
  return 1 + 65534 * p;
}

void Encoder::Encode(int bit) {
  const unsigned int p = hp_adjust_final(Discretize(p_->Predict()));
  if (const char* trace_path = std::getenv("LAB_BITTRACE")) {
    if (!hp_final_bit_trace) hp_final_bit_trace = std::fopen(trace_path, "wbx");
    if (!hp_final_bit_trace) std::abort();
    const unsigned char little_endian_p[2] = {
        static_cast<unsigned char>(p & 255),
        static_cast<unsigned char>((p >> 8) & 255)};
    if (std::fwrite(little_endian_p, 1, 2, hp_final_bit_trace) != 2) std::abort();
  }
  const unsigned int xmid = x1_ + ((x2_ - x1_) >> 16) * p +
      (((x2_ - x1_) & 0xffff) * p >> 16);
  g_lab_cost_bits -= std::log2(bit ? p/65536.0 : (65536.0-p)/65536.0);
  if (bit) {
    x2_ = xmid;
  } else {
    x1_ = xmid + 1;
  }
  p_->Perceive(bit);

  while (((x1_^x2_) & 0xff000000) == 0) {
    WriteByte(x2_ >> 24);
    x1_ <<= 8;
    x2_ = (x2_ << 8) + 255;
  }
}

void Encoder::EncodeRawBit(int bit, unsigned int p) {
  if (p < 1) p = 1;
  if (p > 65534) p = 65534;
  const unsigned int xmid = x1_ + ((x2_ - x1_) >> 16) * p +
      (((x2_ - x1_) & 0xffff) * p >> 16);
  g_lab_cost_bits -= std::log2(bit ? p/65536.0 : (65536.0-p)/65536.0);
  if (bit) {
    x2_ = xmid;
  } else {
    x1_ = xmid + 1;
  }

  while (((x1_^x2_) & 0xff000000) == 0) {
    WriteByte(x2_ >> 24);
    x1_ <<= 8;
    x2_ = (x2_ << 8) + 255;
  }
}

void Encoder::ObserveKnownBit(int bit) {
  p_->Predict();
  p_->Perceive(bit);
}

void Encoder::ObserveKnownByte(unsigned int byte) {
  for (int bit = 7; bit >= 0; --bit) {
    ObserveKnownBit((byte >> bit) & 1);
  }
}

void Encoder::BeginTraceByte(unsigned long long offset, unsigned int actual_byte,
    unsigned int prev4) {
  (void)offset;
  (void)actual_byte;
  (void)prev4;
}

void Encoder::EndTraceByte() {}

void Encoder::Flush() {
  if (hp_final_bit_trace) {
    if (std::fclose(hp_final_bit_trace) != 0) std::abort();
    hp_final_bit_trace = nullptr;
  }
  while (((x1_^x2_) & 0xff000000) == 0) {
    WriteByte(x2_ >> 24);
    x1_ <<= 8;
    x2_ = (x2_ << 8) + 255;
  }
  WriteByte(x2_ >> 24);

  auto* data = reinterpret_cast<const char*>(out_.data());
  os_->write(data, out_.size());
}
