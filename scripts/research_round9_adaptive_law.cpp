#include "research_round9_adaptive_law.h"
#include <algorithm>
#include <cmath>

uint32_t HPCausalAdaptive::Predict(uint32_t native_p, float neural_p,
                                 bool previous_valid) {
  const double ell = std::log(double(native_p)/(65536.0-double(native_p)));
  float feature = 0.0f;
  if (previous_valid) {
    const double nn = std::max(1.0/65536.0,
        std::min(65535.0/65536.0,double(neural_p)));
    feature = float(std::max(-12.0,std::min(12.0,
        std::log(nn/(1.0-nn))-ell))/12.0);
  }
  const double dot = (0.0016181118716570748 +
      (-0.007454085408717222)*ell) + 2.3818512619982752*double(feature);
  const double multipliers[4] = {0.5,1.0,1.5,2.0};
  experts_[0] = native_p;
  for (int k=1;k<5;k++) {
    const double z=ell+multipliers[k-1]*dot;
    const double prob = z>=0 ? 1.0/(1.0+std::exp(-z))
                            : std::exp(z)/(1.0+std::exp(z));
    experts_[k]=uint32_t(std::max(1.0,std::min(65535.0,
        std::floor(65536.0*prob+0.5))));
  }
  double mixture=0.0;
  for(int k=0;k<5;k++) mixture+=weights_[k]*double(experts_[k])/65536.0;
  pending_=true;
  return uint32_t(std::max(1.0,std::min(65535.0,
      std::floor(65536.0*mixture+0.5))));
}

void HPCausalAdaptive::Observe(int bit) {
  if(!pending_) return;
  constexpr double epsilon=2.6441431586476938e-06;
  double total=0.0;
  for(int k=0;k<5;k++) {
    const double pk=bit ? double(experts_[k])/65536.0
                       : 1.0-double(experts_[k])/65536.0;
    weights_[k]*=pk;
    total+=weights_[k];
  }
  for(int k=0;k<5;k++)
    weights_[k]=(1.0-epsilon)*weights_[k]/total+epsilon/5.0;
  pending_=false;
}

#ifdef HP_ADAPTIVE_REPLAY_MAIN
#include <cstdio>
int main(int argc,char**argv) {
  if(argc!=6) return 2;
  FILE *input=std::fopen(argv[1],"rb"),*pp=std::fopen(argv[2],"rb"),
       *hp=std::fopen(argv[3],"rb"),*stage=std::fopen(argv[4],"rb"),
       *out=std::fopen(argv[5],"wb");
  if(!input||!pp||!hp||!stage||!out) return 3;
  if(std::fseek(stage,12,SEEK_SET)) return 4;
  HPCausalAdaptive law;
  unsigned char h[193]; bool valid=false; int ch;
  while((ch=std::fgetc(input))!=EOF) {
    for(int b=7;b>=0;b--) {
      uint16_t p; float sources[19];
      if(std::fread(&p,2,1,pp)!=1 || std::fread(sources,4,19,stage)!=19)
        return 5;
      uint16_t q=uint16_t(law.Predict(p,sources[17],valid));
      if(std::fwrite(&q,2,1,out)!=1) return 6;
      law.Observe((ch>>b)&1);
    }
    if(std::fread(h,1,193,hp)!=193) return 7;
    valid=h[0]!=0;
  }
  std::fclose(out);
  return 0;
}
#endif
