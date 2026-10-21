#pragma once
#include <array>
#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include "probability_tables.inc"

namespace hp {
// Tables are frozen integer assets. No libm operation occurs in coding.
inline int32_t stretch(uint32_t p) { return kStretch[std::clamp(p,1u,65535u)]; }
inline uint16_t squash(int64_t z) { return kSquash[std::clamp<int64_t>(z,-4096,4096)+4096]; }
inline uint16_t apply_odds(uint16_t native,int64_t correction) {
  uint64_t ratio=kOdds[std::clamp<int64_t>(correction,-2048,2048)+2048];
  uint64_t numerator=uint64_t(native)*ratio;
  uint64_t denominator=numerator+uint64_t(65536u-native)*(1ULL<<20);
  // The frozen +/-8 log-odds limit makes the rounded Q16 numerator fit uint64.
  uint64_t q=(numerator*65536+denominator/2)/denominator;
  return uint16_t(std::clamp<uint64_t>(q,1,65535));
}
inline int64_t round_signed(int64_t n,int64_t d) {
  if(d<=0)throw std::invalid_argument("nonpositive denominator");
  return n>=0 ? (n+d/2)/d : -((-n+d/2)/d);
}
inline uint64_t isqrt(uint64_t n) {
  uint64_t root=0,bit=1ULL<<62;
  while(bit>n)bit>>=2;
  while(bit) { if(n>=root+bit) { n-=root+bit;root=(root>>1)+bit; } else root>>=1;bit>>=2; }
  return root;
}
class OnlineMixer {
 public:
  static constexpr int kContexts=640,kFeatures=16;
  using Count=uint64_t; // The full canonical stream has more than 2^32 bits.
  explicit OnlineMixer(bool neural=true,bool shuffled=false,bool identity=false,uint32_t rate=1000)
      : neural_(neural),shuffled_(shuffled),identity_(identity),rate_(rate) {
    if(rate>1000000)throw std::invalid_argument("rate exceeds fixed-point safety contract");
    for(auto &row:weights_) { row.fill(0); row[0]=1<<24; }
  }
  uint16_t Predict(uint16_t native,uint16_t nn,const std::array<uint16_t,14>& other,
                   unsigned bitpos,unsigned previous_class,bool nn_valid) {
    if(pending_)throw std::logic_error("Predict without Observe");
    if(bitpos>=8||previous_class>=10||native==0||nn==0)throw std::invalid_argument("invalid inputs");
    unsigned confidence=std::max(unsigned(nn),65536u-unsigned(nn));
    unsigned bucket=0;constexpr unsigned thresholds[7]={49152,57344,61440,63488,64512,65024,65280};
    if(neural_&&nn_valid)for(auto threshold:thresholds)bucket+=confidence>=threshold;
    context_=global_context_?0:(bitpos*8+bucket)*10+previous_class;
    if(shuffled_)context_=(context_*173+37)%kContexts; // relabeling only; not a semantic null
    features_[0]=stretch(native); features_[1]=neural_&&nn_valid?stretch(nn):0;
    for(int i=0;i<13;i++)features_[i+2]=stretch(other[i]);
    features_[15]=256; // constant; other[13] deliberately unused
    const auto &w=weights_[context_];bool unchanged=w[0]==1<<24;
    for(int i=1;i<kFeatures;i++)unchanged=unchanged&&w[i]==0;
    int64_t sum=0;for(int i=0;i<kFeatures;i++)sum+=int64_t(w[i])*features_[i];
    int64_t correction=round_signed(sum-int64_t(1<<24)*features_[0],1<<24);
    probability_=identity_||unchanged?native:apply_odds(native,correction);
    pending_=true;return probability_;
  }
  // This merges contexts rather than just renaming identical context states.
  void SetGlobalContext(bool enabled) {
    if(pending_)throw std::logic_error("context mode change during pending bit");
    global_context_=enabled;
  }
  void Observe(unsigned bit) {
    if(!pending_||bit>1)throw std::logic_error("invalid observation");
    if(!identity_&&rate_) {
      auto &w=weights_[context_];Count n=++counts_[context_];
      // eta0=rate/1e6, slowed once per 4096 observations of this context.
      // Error Q16 * features Q8 is Q24. Q24 master coefficients preserve
      // small updates after long histories; rounding each update to Q12 would
      // artificially freeze late learning. This is a straight-through update
      // for the discretized/clipped law, not an exact discrete-loss gradient.
      int64_t denom=1000000LL*(1+isqrt(n/4096));
      int64_t error=int64_t(bit)*65536-probability_;
      for(int i=0;i<kFeatures;i++) {
        int64_t change=round_signed(error*features_[i]*int64_t(rate_),denom);
        w[i]=int32_t(std::clamp<int64_t>(int64_t(w[i])+change,-int64_t(4<<24),int64_t(4<<24)));
      }
    }
    pending_=false;
  }
 private:
  std::array<std::array<int32_t,kFeatures>,kContexts> weights_{};
  std::array<Count,kContexts> counts_{};
  std::array<int32_t,kFeatures> features_{};
  unsigned context_=0;uint16_t probability_=32768;
  bool pending_=false,global_context_=false,neural_,shuffled_,identity_;uint32_t rate_;
};
}
