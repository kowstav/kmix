#pragma once
#include "integer_mixer.h"

namespace hp {
// Four exact, causal horizons of two orthogonal hidden-state projections.
// Q8 observations are retained in Q28 accumulators so a 131072-byte horizon
// does not freeze because its integer update is below a Q8 unit.
class LongMemory {
 public:
  static constexpr unsigned kShifts[4]={0,10,15,17};
  void Reset() {means_={};last_={};}
  void UpdateHidden(const unsigned char* row) {
    for(unsigned projection=0;projection<2;projection++) {
      int64_t sum=0;
      for(unsigned i=0;row[0]!=0&&i<192;i++) {
        int sign=((i>>(projection?3:0))&1)?-1:1;
        sum+=sign*(2*int(row[i+1])-255);
      }
      int64_t value=std::clamp<int64_t>(round_signed(sum*16,192),-4096,4096);
      last_[projection]=int32_t(value);
      for(unsigned j=0;j<4;j++) {
        int64_t target=value*(1LL<<20);
        means_[projection][j]+=round_signed(target-means_[projection][j],1LL<<kShifts[j]);
      }
    }
  }
  std::array<uint16_t,8> Features() const {
    std::array<uint16_t,8> result{};
    for(unsigned i=0;i<2;i++)for(unsigned j=0;j<4;j++)
      result[i*4+j]=squash(std::clamp<int64_t>(round_signed(means_[i][j],1LL<<20)-last_[i],-4096,4096));
    return result;
  }
 private:
  std::array<std::array<int64_t,4>,2> means_{};
  std::array<int32_t,2> last_{};
};
}
