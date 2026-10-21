#include "integer_mixer.h"
#include "fixed_share_integer.h"
#include "long_memory.h"
#include "wrt_classes.h"
#include <cstdio>
int main() {
  static_assert(hp::OnlineMixer::kFeatures==24);
  for(unsigned c=0;c<256;c++) {
    if(hp::InverseWrtByte(hp::InverseWrtByte(c))!=c)return 1;
    if(hp::PreviousWrtClass(c)>=10)return 2;
  }
  if(hp::PreviousWrtClass('L')!=7||hp::PreviousWrtClass('N')!=7)return 3;
  hp::OnlineMixer a(true,false,false,250),b(true,false,false,250);
  std::array<uint16_t,14> source;source.fill(51000);
  std::array<uint16_t,8> neutral;neutral.fill(32768);
  for(unsigned t=0;t<32768;t++) {
    const unsigned native=1+(t*137)%65535,nn=1+(t*223)%65535;
    auto p=a.Predict(native,nn,source,t%8,(t/8)%10,true);
    auto q=b.Predict(native,nn,source,t%8,(t/8)%10,true,neutral);
    if(p!=q)return 4;
    unsigned y=(t*13)%19<9;a.Observe(y);b.Observe(y);
  }
  hp::FixedShareInteger<4> first,second;
  for(unsigned t=0;t<65536;t++) {
    std::array<uint16_t,4> p={uint16_t(1+t%65535),uint16_t(65535-t%65535),1,65535};
    auto u=first.Predict(p),v=second.Predict(p);if(!u||u!=v)return 5;
    if(u<*std::min_element(p.begin(),p.end())||u>*std::max_element(p.begin(),p.end()))return 6;
    unsigned y=t%17<9;first.Observe(y);second.Observe(y);
  }
  hp::LongMemory m;unsigned char row[193]={1};
  for(unsigned i=0;i<192;i++)row[i+1]=(i&1)?0:255;
  for(unsigned i=0;i<400000;i++)m.UpdateHidden(row);
  const auto active=m.Features();row[0]=0;
  // A reset row is not stale hidden data. Its decay clock advances.
  m.UpdateHidden(row);const auto one=m.Features();
  if(active==one)return 7;
  for(unsigned i=0;i<2000000;i++)m.UpdateHidden(row);
  for(auto p:m.Features())if(std::abs(int(p)-32768)>256)return 8;
  std::puts("PASS add-only neutral memory, remapped byte classes, deterministic positive guard and reset-row decay");
}
