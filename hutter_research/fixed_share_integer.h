#pragma once
#include "integer_mixer.h"

namespace hp {
// Deterministic Q32 posterior. Ideal Bayesian regret bounds require additional
// posterior/probability rounding terms; they are not asserted for this codec.
template<unsigned K> class FixedShareInteger {
 public:
  FixedShareInteger() { for(auto& w:w_)w=uint64_t(1)<<32; }
  uint16_t Predict(const std::array<uint16_t,K>& p) {
    if(pending_)throw std::logic_error("guard Predict without Observe");
    p_=p;unsigned __int128 numerator=0;uint64_t total=0;
    for(unsigned i=0;i<K;i++) {
      if(!p[i])throw std::invalid_argument("zero expert probability");
      numerator+=static_cast<unsigned __int128>(w_[i])*p[i]; total+=w_[i];
    }
    pending_=true;
    return uint16_t(std::clamp<uint64_t>(uint64_t((numerator+total/2)/total),1,65535));
  }
  void Observe(unsigned y) {
    if(!pending_||y>1)throw std::logic_error("guard invalid observation");
    std::array<uint64_t,K> product{};uint64_t denominator=0;
    for(unsigned i=0;i<K;i++){product[i]=w_[i]*(y?p_[i]:65536u-p_[i]);denominator+=product[i];}
    constexpr uint64_t mass=uint64_t(K)<<32;
    for(unsigned i=0;i<K;i++) {
      uint64_t posterior=uint64_t(static_cast<unsigned __int128>(product[i])*mass/denominator);
      // share epsilon=2^-20, uniform restart; deterministic floors are paid.
      w_[i]=std::max<uint64_t>(1,posterior-(posterior>>20)+((uint64_t(1)<<32)>>20));
    }
    pending_=false;
  }
 private:
  std::array<uint64_t,K> w_{};std::array<uint16_t,K> p_{};bool pending_=false;
};
}
