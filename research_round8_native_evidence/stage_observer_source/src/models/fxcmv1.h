//#ifndef FXCM_H
//#define FXCM_H

#include "model.h"
#include <vector>
#include <memory>

// lext_big knob FXCM_TF_MIXER (compile-time -D, unset/0 = fxcm_v26 unchanged):
// a 19th layer-1 mixer mxA[18] whose weight set is selected by the
// transformer's expected byte (lstmex), as fx2-cmix's fxcmv1 mxA[9] was.
// 1 = fx2's context (bpos, last two fails, lstmex); 2 = additionally a
// 4-level confidence bucket of the transformer's bit prediction (lstmconf).
#ifndef FXCM_TF_MIXER
#define FXCM_TF_MIXER 0
#endif
#if FXCM_TF_MIXER < 0 || FXCM_TF_MIXER > 2
#error "FXCM_TF_MIXER must be unset/0 (off), 1 (fx2 context) or 2 (fx2 context + confidence bucket)"
#endif

namespace fxcmv1 {
  class Predictor{

public:
  Predictor();
  int p() ;
  void update();
  void FreeMemory();
};
}

class FXCM : public Model {
 public:
  FXCM();
  const std::valarray<float>& Predict() const;
  const short* RawPredictions() const;
  const unsigned char* PredictionMask() const;
  unsigned int ActivePredictions() const;
  float RawPredictionProbability(short raw) const;
  unsigned int NumOutputs();
  void Perceive(int bit);
  void ByteUpdate() {};
  void FreeMemory();

 private:
  std::unique_ptr<fxcmv1::Predictor> predictor_;
};

//#endif
