#ifndef HP_CALIBRATION_ODDS_H
#define HP_CALIBRATION_ODDS_H
#include <cstdint>
#include <cstdio>
#include <cstdlib>
static unsigned hp_coded_bit_position=0;
static unsigned hp_adjust_final(unsigned p){
 static uint32_t factor[128];static bool initialized=false;
 if(!initialized){for(auto &v:factor)v=1u<<20;
  if(const char *path=std::getenv("LAB_ODDS")){FILE*f=std::fopen(path,"rb");if(!f)std::abort();
   for(auto &v:factor){unsigned char b[4];if(std::fread(b,1,4,f)!=4)std::abort();v=uint32_t(b[0])|(uint32_t(b[1])<<8)|(uint32_t(b[2])<<16)|(uint32_t(b[3])<<24);if(v<800000||v>1400000)std::abort();}
   if(std::fgetc(f)!=EOF)std::abort();std::fclose(f);
  }initialized=true;
 }
 uint32_t f=factor[(hp_coded_bit_position++&7)*16+(p>>12)];
 uint64_t a=uint64_t(p)*f,b=uint64_t(65536-p)*(1u<<20),den=a+b;
 unsigned q=unsigned((a*65536+den/2)/den);return q<1?1:q>65535?65535:q;
}
#endif
