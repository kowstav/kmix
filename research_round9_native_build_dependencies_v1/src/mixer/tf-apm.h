#ifndef TF_APM_H
#define TF_APM_H

// lext_big knob LEXT_TF_APM (compile-time, -DLEXT_TF_APM=<mode>; unset/0 =
// cmix-lex-transformer unchanged). An interpolating APM / SSE stage on the
// pretrained transformer's bit prediction (byte_mixer_output), the dominant
// input of the final mixers, which today reaches them only as one stretched
// value per layer and never enters the SSE contexts:
//   mode 1: FINAL refinement. After cmix's SSE, p is refined by an APM whose
//           context is (16-bucket stretch(p_tf), bit position, tf-agrees-with-p
//           flag) and averaged: p' = (p + 3 * apm(p)) / 4 (paq8 style).
//   mode 2: EXTRA INPUT. apm(p_tf | context = partial byte (bit_context 1..255)
//           x 4-bucket |stretch(p_tf)| class) is one more input of both mixer
//           layers, next to the raw p_tf.
//   mode 3: both.
// Float arithmetic in a fixed order, no randomness: identical on the
// compression and decompression sides (same binary).
#ifndef LEXT_TF_APM
#define LEXT_TF_APM 0
#endif
#if LEXT_TF_APM < 0 || LEXT_TF_APM > 3
#error "LEXT_TF_APM must be unset/0, 1 (final refinement), 2 (extra mixer input) or 3 (both)"
#endif

#include <math.h>

#include <vector>

// 33 knots over stretch(p) in [-8, 8] (step 0.5), linear interpolation
// between the two nearest knots; both knots move towards the coded bit with
// an adaptive rate 1/(n+1.5) that floors at `rate` (paq8 APM with a
// count-based warm-up, in floats).
class TfApm {
 public:
  TfApm(int n_ctx, float rate) : t_(n_ctx * 33), n_(n_ctx * 33, 0), rate_(rate) {
    for (int c = 0; c < n_ctx; ++c)
      for (int j = 0; j < 33; ++j)
        t_[c * 33 + j] = 1.0f / (1.0f + expf(-((j - 16) * 0.5f)));
  }
  float Predict(float p, int ctx) {
    if (p < 1e-6f) p = 1e-6f;
    if (p > 1.0f - 1e-6f) p = 1.0f - 1e-6f;
    float s = logf(p / (1.0f - p));
    if (s < -7.999f) s = -7.999f;
    if (s > 7.999f) s = 7.999f;
    float pos = (s + 8.0f) * 2.0f;
    int j = (int)pos;
    w_ = pos - j;
    idx_ = ctx * 33 + j;
    return t_[idx_] * (1.0f - w_) + t_[idx_ + 1] * w_;
  }
  void Update(int bit) {
    Upd(idx_, bit);
    Upd(idx_ + 1, bit);
  }
  static float Stretch(float p) {
    if (p < 1e-6f) p = 1e-6f;
    if (p > 1.0f - 1e-6f) p = 1.0f - 1e-6f;
    return logf(p / (1.0f - p));
  }

 private:
  void Upd(int i, int bit) {
    float r = 1.0f / (n_[i] + 1.5f);
    if (r < rate_) r = rate_;
    t_[i] += ((float)bit - t_[i]) * r;
    if (n_[i] < 65535) ++n_[i];
  }
  std::vector<float> t_;
  std::vector<unsigned short> n_;
  float rate_;
  int idx_ = 0;
  float w_ = 0.0f;
};

#endif  // TF_APM_H
