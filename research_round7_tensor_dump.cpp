// Research verification helper: use the production C++ loader independently of
// the Python codec, and serialize all decoded tensor bytes in sorted name order.
#include "weights_io.h"
#include <cstdio>
#include <algorithm>
#include <vector>
#include <string>
#include <cstdlib>
static void u32(FILE* f,uint32_t x){if(std::fwrite(&x,4,1,f)!=1)std::abort();}
int main(int argc,char** argv){
  if(argc!=3)return 2;
  auto wf=fx2::WeightsFile::load_compressed(argv[1]);
  std::vector<std::string> names;
  for(auto& e:wf.tensors)names.push_back(e.first);
  std::sort(names.begin(),names.end());
  FILE* f=std::fopen(argv[2],"wb");if(!f)return 3;
  std::fwrite("FX2TFW01",1,8,f);u32(f,names.size());
  size_t bytes=0;
  for(auto& name:names){auto& t=wf.tensors.at(name);
    u32(f,name.size());std::fwrite(name.data(),1,name.size(),f);
    std::fwrite(&t.dtype,1,1,f);u32(f,t.shape.size());
    for(auto d:t.shape)u32(f,d);
    if(std::fwrite(t.data.data(),1,t.data.size(),f)!=t.data.size())return 4;
    bytes+=t.data.size();
  }
  if(std::fclose(f))return 5;
  std::printf("DUMPED %zu tensors, %zu tensor bytes\n",names.size(),bytes);
}
