// Corrected, add-only memory comparisons. Twelve finite all-target arms are
// evaluated together; native encoder history is unchanged. No traces deleted.
#include "integer_mixer.h"
#include "long_memory.h"
#include "wrt_classes.h"
#include "fixed_share_integer.h"
#include "stream_reader.h"
#include <cstdio>
#include <cmath>
#include <fstream>
#include <iterator>
#include <vector>

static uint16_t Q16(float p) {
  if(!std::isfinite(p))throw std::invalid_argument("nonfinite probability");
  return uint16_t(std::clamp<int64_t>(int64_t(double(p)*65536+.5),1,65535));
}
static uint16_t FromLogit(float z) {
  if(!std::isfinite(z))throw std::invalid_argument("nonfinite logit");
  double v=std::clamp(double(z)*256,-4096.,4096.);
  return hp::squash(v>=0?int64_t(v+.5):-int64_t(-v+.5));
}
int main(int argc,char** argv) {
  if(argc!=9){std::fprintf(stderr,"input final_p stage hidden done out window abs_offset\n");return 2;}
  FILE* output=std::fopen(argv[6],"wx");if(!output)return 3;
  try {
    uint64_t window=std::stoull(argv[7]),absolute=std::stoull(argv[8]);
    if(!window)throw std::invalid_argument("zero window");
    std::ifstream f(argv[1],std::ios::binary);if(!f)throw std::runtime_error("input missing");
    std::vector<unsigned char> data((std::istreambuf_iterator<char>(f)),{});
    hp::TailReader native(argv[2],argv[5]),stage(argv[3],argv[5]),hidden(argv[4],argv[5]);
    char magic[8];uint32_t width;
    if(!stage.Read(magic,8)||std::memcmp(magic,"HPSTG001",8)||!stage.Read(&width,4)||width!=19)
      throw std::runtime_error("invalid stage header");
    constexpr unsigned M=10,K=12;
    const char* names[K]={"identity","full_250","full_1000","full_4000","global_250",
      "no_explicit_nn_250","reduced_250","add_memory_250","memory_zero_250","short_memory_250",
      "guard_4_fixedshare","guard_memory_pair"};
    std::vector<hp::OnlineMixer> models;models.reserve(M);
    for(unsigned i=0;i<M;i++)models.emplace_back(i!=5,false,i==0,i==2?1000:i==3?4000:250);
    models[4].SetGlobalContext(true);
    hp::LongMemory memory,short_memory;hp::FixedShareInteger<4> guard;hp::FixedShareInteger<2> memguard;
    std::array<uint16_t,8> neutral;neutral.fill(32768);
    std::vector<double> loss(65536);
    for(unsigned i=1;i<65536;i++)loss[i]=-std::log2(double(i)/65536);
    std::array<long double,K> total{},block{};
    long double base=0,blockbase=0;uint64_t n=0,begin=0,identity_bad=0,memory_zero_bad=0;
    bool valid=false;unsigned previous=9;
    auto flush=[&](bool partial){
      std::fprintf(output,"{\"type\":\"window\",\"abs_offset\":%llu,\"history_bytes\":%llu,\"bytes\":%llu,\"partial\":%s,\"baseline_bits\":%.9Lf,\"arms\":{",
        (unsigned long long)(absolute+begin),(unsigned long long)begin,(unsigned long long)(n-begin),partial?"true":"false",blockbase);
      for(unsigned a=0;a<K;a++)std::fprintf(output,"%s\"%s\":%.9Lf",a?",":"",names[a],block[a]);
      std::fprintf(output,"}}\n");std::fflush(output);block={};blockbase=0;begin=n;
    };
    for(;n<data.size();) {
      uint16_t p[8];float rows[8][19];unsigned char h[193];bool complete=true;
      for(unsigned b=0;b<8&&complete;b++)complete=native.Read(&p[b],2)&&stage.Read(rows[b],76);
      if(!complete||!hidden.Read(h,193))break;
      if(n%128==0)short_memory.Reset();
      const auto mem=memory.Features(),shortmem=short_memory.Features();
      for(unsigned b=0;b<8;b++) {
        if(!p[b])throw std::runtime_error("zero native Q16");
        std::array<uint16_t,14> sources;sources.fill(32768);sources[0]=Q16(rows[b][14]);
        for(unsigned i=0;i<12;i++)sources[i+1]=FromLogit(rows[b][i]);
        std::array<uint16_t,K> q{};
        for(unsigned a=0;a<M;a++) {
          auto src=sources;if(a==6)for(unsigned i=5;i<13;i++)src[i]=32768;
          const auto& extra=a==7?mem:a==9?shortmem:neutral;
          q[a]=models[a].Predict(p[b],Q16(rows[b][17]),src,b,previous,valid,extra);
        }
        q[10]=guard.Predict({p[b],q[1],q[4],q[6]});
        q[11]=memguard.Predict({q[8],q[7]});
        identity_bad+=q[0]!=p[b];memory_zero_bad+=q[8]!=q[1];
        unsigned y=(data[n]>>(7-b))&1;
        double cost=loss[y?p[b]:65536u-p[b]];base+=cost;blockbase+=cost;
        for(unsigned a=0;a<K;a++){double c=loss[y?q[a]:65536u-q[a]];total[a]+=c;block[a]+=c;}
        for(auto& model:models)model.Observe(y);
        guard.Observe(y);memguard.Observe(y);
      }
      valid=h[0]!=0;previous=hp::PreviousWrtClass(data[n]);memory.UpdateHidden(h);short_memory.UpdateHidden(h);
      n++;if(n-begin==window)flush(false);
    }
    if(n>begin)flush(true);
    std::fprintf(output,"{\"type\":\"summary\",\"bytes\":%llu,\"input_bytes\":%zu,\"baseline_bits\":%.9Lf,\"identity_mismatch_bits\":%llu,\"memory_zero_mismatch_bits\":%llu,\"totals\":{",
       (unsigned long long)n,data.size(),base,(unsigned long long)identity_bad,(unsigned long long)memory_zero_bad);
    for(unsigned a=0;a<K;a++)std::fprintf(output,"%s\"%s\":%.9Lf",a?",":"",names[a],total[a]);
    std::fprintf(output,"}}\n");std::fclose(output);
    return identity_bad||memory_zero_bad?12:0;
  }catch(const std::exception& e){std::fprintf(stderr,"%s\n",e.what());std::fclose(output);return 11;}
}
