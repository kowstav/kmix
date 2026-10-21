#pragma once
#include "integer_mixer.h"
#include "fixed_share_integer.h"
#include "wrt_classes.h"
#include <cmath>

#ifndef HP_R13_HEAD
#define HP_R13_HEAD 0
#endif
static_assert(HP_R13_HEAD>=0 && HP_R13_HEAD<=2,"unsupported finite native arm");
namespace hp {
// Mode 0 preserves the native float-to-coder operation. Modes 1/2 return
// integer probabilities directly to BOTH coders; a second float discretization
// would alter the law. All native model updates still use their own predictions.
class NativeFinalHead {
 public:
  static uint16_t NativeQ(float p) {return uint16_t(1+65534*p);}
  static uint16_t FeatureQ(float p) {
    if(!std::isfinite(p))throw std::invalid_argument("nonfinite feature");
    return uint16_t(std::clamp<int64_t>(int64_t(double(p)*65536+.5),1,65535));
  }
  static uint16_t LogitQ(float z) {
    if(!std::isfinite(z))throw std::invalid_argument("nonfinite logit");
    double v=std::clamp(double(z)*256,-4096.,4096.);
    return squash(v>=0?int64_t(v+.5):-int64_t(-v+.5));
  }
  template<class Inputs> void Capture(float presSE,float nn,const Inputs& layer,unsigned count) {
#if HP_R13_HEAD
    if(count!=14)throw std::invalid_argument("native head requires pinned 14 inputs");
    sources_.fill(32768);sources_[0]=FeatureQ(presSE);
    for(unsigned i=0;i<12;i++)sources_[i+1]=LogitQ(layer[i]);
    nn_=FeatureQ(nn);
#else
    (void)presSE;(void)nn;(void)layer;(void)count;
#endif
  }
  uint16_t Predict(float p) {
    const auto native=NativeQ(p);
#if HP_R13_HEAD
    if(pending_)throw std::logic_error("native head missing observation");
    if(!initialized_){global_.SetGlobalContext(true);initialized_=true;}
    auto sources=sources_;for(unsigned i=5;i<13;i++)sources[i]=32768;
    const auto a=full_.Predict(native,nn_,sources_,bit_,previous_,valid_);
    const auto b=global_.Predict(native,nn_,sources_,bit_,previous_,valid_);
    const auto c=reduced_.Predict(native,nn_,sources,bit_,previous_,valid_);
    const auto guarded=guard_.Predict({native,a,b,c});
    pending_=true;return HP_R13_HEAD==1?a:guarded;
#else
    return native;
#endif
  }
  void Observe(unsigned y) {
#if HP_R13_HEAD
    if(!pending_||y>1)throw std::logic_error("native head invalid observation");
    full_.Observe(y);global_.Observe(y);reduced_.Observe(y);guard_.Observe(y);
    byte_=(byte_<<1)|y;if(++bit_==8){previous_=PreviousWrtClass(byte_);bit_=0;byte_=0;}
    pending_=false;
#else
    (void)y;
#endif
  }
  void SetNextByteNeuralValid(bool value) {
#if HP_R13_HEAD
    valid_=value;
#else
    (void)value;
#endif
  }
 private:
#if HP_R13_HEAD
  OnlineMixer full_{true,false,false,250},global_{true,false,false,250},reduced_{true,false,false,250};
  FixedShareInteger<4> guard_;
  std::array<uint16_t,14> sources_{};
  uint16_t nn_=32768;unsigned bit_=0,byte_=0,previous_=9;
  bool pending_=false,initialized_=false,valid_=false;
#endif
};
}
