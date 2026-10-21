#include "integer_mixer.h"
#include "long_memory.h"
#include <cstdio>
#include <cmath>
#include <limits>
int main() {
  for(unsigned p=1;p<65536;p++) {
    hp::OnlineMixer identity(true,false,true);
    std::array<uint16_t,14> o;o.fill(32768);
    if(identity.Predict(p,p,o,0,0,true)!=p)return 1;
    if(hp::apply_odds(p,0)!=p||hp::apply_odds(p,256)<p||hp::apply_odds(p,-256)>p)return 7;
    identity.Observe(p&1);
  }
  for(uint32_t n=0;n<100000;n++) {uint64_t s=hp::isqrt(n);if(s*s>n||(s+1)*(s+1)<=n)return 2;}
  for(uint64_t n:{uint64_t(1)<<32,uint64_t(1)<<48,std::numeric_limits<uint64_t>::max()}) {
    uint64_t s=hp::isqrt(n);
    if(s*s>n||(s+1)<=n/(s+1))return 4;
  }
  static_assert(std::numeric_limits<hp::OnlineMixer::Count>::max()>8ULL*587138826ULL);
  hp::OnlineMixer a,b;std::array<uint16_t,14> sources;sources.fill(40000);
  for(unsigned t=0;t<4096;t++) {
    auto p=a.Predict(20000,50000,sources,t%8,(t/8)%10,true);
    auto q=b.Predict(20000,50000,sources,t%8,(t/8)%10,true);
    if(p!=q||!p)return 3;
    unsigned y=(t*17+3)%11<7;a.Observe(y);b.Observe(y);
  }
  hp::LongMemory memory;unsigned char hidden[193]={1};
  for(unsigned i=0;i<192;i++)hidden[i+1]=(i&1)?0:255;
  for(unsigned i=0;i<131072;i++)memory.UpdateHidden(hidden);
  // Analytic EWMA under constant input: m_n=v*(1-(1-1/tau)^n).
  double contrast=-4080*std::exp(131072*std::log1p(-1.0/131072));
  uint16_t expected=hp::squash(int64_t(std::round(contrast)));
  if(std::abs(int(memory.Features()[3])-int(expected))>1)return 5;
  memory.Reset();for(auto p:memory.Features())if(p!=32768)return 6;
  std::printf("PASS exhaustive neutral Q16, uint64 counters/sqrt, deterministic online state and analytic long retention; mixer_state=%zu memory_state=%zu bytes\n",sizeof(hp::OnlineMixer),sizeof(hp::LongMemory));
}
