// Finite causal replay against an unchanged native trajectory. Archive and
// production timing qualification are separate, mandatory promotion gates.
#include "integer_mixer.h"
#include "long_memory.h"
#include "wrt_classes.h"
#include <cstdio>
#include <cstring>
#include <cmath>
#include <limits>

static unsigned previous_class(unsigned byte) {
  if(byte==' ')return 0;
  if(byte=='\n')return 1;
  if(byte>=128)return 2;
  if(byte>='a'&&byte<='z')return 3;
  if(byte>='A'&&byte<='Z')return 4;
  if(byte>='0'&&byte<='9')return 5;
  if(byte<32)return 6;
  if(byte=='<'||byte=='>'||byte=='['||byte==']')return 7;
  if(byte=='.'||byte==','||byte==';'||byte==':')return 8;
  return 9;
}
static uint16_t q16(float p) {
  if(!std::isfinite(p))throw std::invalid_argument("nonfinite stage probability");
  if(p<=0)return 1;if(p>=1)return 65535;
  // Scaling by a power of two is exact for these finite FP32 probabilities.
  return uint16_t(std::clamp(uint32_t(double(p)*65536.0+0.5),1u,65535u));
}
static uint16_t from_logit(float z) {
  if(!std::isfinite(z))throw std::invalid_argument("nonfinite stage logit");
  double value=std::clamp(double(z)*256.0,-4096.0,4096.0);
  int64_t quantized=value>=0?int64_t(value+0.5):-int64_t(-value+0.5);
  return hp::squash(quantized);
}
int main(int argc,char**argv) {
  // input native_p hidden stage output arm learning_rate
  if(argc!=8){std::fprintf(stderr,"input native_p hidden stage output arm learning_rate\n");return 2;}
  FILE *input=std::fopen(argv[1],"rb"),*native=std::fopen(argv[2],"rb"),
       *hidden=std::fopen(argv[3],"rb"),*stage=std::fopen(argv[4],"rb"),
       *output=std::fopen(argv[5],"wb");
  if(!input||!native||!hidden||!stage||!output)return 3;
  char magic[8];uint32_t width=0;
  if(std::fread(magic,1,8,stage)!=8||std::memcmp(magic,"HPSTG001",8)||
     std::fread(&width,4,1,stage)!=1||width!=19)return 4;
  std::string arm=argv[6];
  bool use_memory=arm=="long_memory"||arm=="short_memory"||arm=="memory_zero";
  if(arm!="identity"&&arm!="full"&&arm!="no_explicit_nn"&&arm!="global"&&arm!="relabel"&&!use_memory)return 9;
  unsigned long rate=std::stoul(argv[7]);
  if(rate>1000000)return 10;
  hp::OnlineMixer model(arm!="no_explicit_nn",arm=="relabel",arm=="identity",uint32_t(rate));
  model.SetGlobalContext(arm=="global");
  hp::LongMemory memory;
  bool valid=false;unsigned prior_class=9;uint64_t bytes=0;int ch;
  long double base_bits=0,candidate_bits=0;
  try {
    while((ch=std::fgetc(input))!=EOF) {
      if(arm=="short_memory"&&bytes%128==0)memory.Reset();
      for(unsigned bitpos=0;bitpos<8;bitpos++) {
        uint16_t p=0;float row[19];
        if(std::fread(&p,2,1,native)!=1||std::fread(row,4,19,stage)!=19)return 5;
        std::array<uint16_t,14> sources;sources.fill(32768);
        sources[0]=q16(row[14]); // pre-SSE probability
        for(unsigned i=0;i<12;i++)sources[i+1]=from_logit(row[i]);
        std::array<uint16_t,8> mem;mem.fill(32768);
        if(use_memory&&arm!="memory_zero")mem=memory.Features();
        uint16_t q=model.Predict(p,q16(row[17]),sources,bitpos,prior_class,valid,mem);
        if(std::fwrite(&q,2,1,output)!=1)return 6;
        unsigned y=(unsigned(ch)>>(7-bitpos))&1;
        // libm here scores a diagnostic, never selects or updates a probability.
        base_bits-=std::log2((y?p:65536u-p)/65536.0L);
        candidate_bits-=std::log2((y?q:65536u-q)/65536.0L);
        model.Observe(y);
      }
      unsigned char h[193];if(std::fread(h,1,193,hidden)!=193)return 7;
      valid=h[0]!=0;prior_class=hp::PreviousWrtClass(unsigned(ch));bytes++;
      if(use_memory)memory.UpdateHidden(h);
    }
    if(std::fgetc(native)!=EOF||std::fgetc(hidden)!=EOF||std::fgetc(stage)!=EOF)return 8;
  } catch(const std::exception& e){std::fprintf(stderr,"%s\n",e.what());return 11;}
  std::fclose(output);
  std::printf("{\"bytes\":%llu,\"baseline_bits\":%.12Lf,\"candidate_bits\":%.12Lf,\"gain_byte_equivalent\":%.12Lf,\"state_bytes\":%zu,\"qualification\":\"replay_only\"}\n",
      (unsigned long long)bytes,base_bits,candidate_bits,(base_bits-candidate_bits)/8,sizeof(model));
  return 0;
}
