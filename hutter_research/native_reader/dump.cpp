#include "weights_io.h"
#include <cstdio>
#include <algorithm>
#include <cstring>
#include <string>
int main(int argc,char** argv) {
  if(argc!=3)return 2;
  FILE* probe=std::fopen(argv[1],"rb");if(!probe)return 3;
  char magic[8];if(std::fread(magic,1,8,probe)!=8){std::fclose(probe);return 4;}std::fclose(probe);
  auto w=std::memcmp(magic,"FX2TFW01",8)==0?fx2::WeightsFile::load(argv[1]):fx2::WeightsFile::load_compressed(argv[1]);
  FILE* f=std::fopen(argv[2],"wbx");if(!f)return 5;
  std::fwrite("FX2TFW01",1,8,f);uint32_t n=w.tensors.size();std::fwrite(&n,4,1,f);
  std::vector<std::string> names;for(auto& p:w.tensors)names.push_back(p.first);std::sort(names.begin(),names.end());
  for(auto& name:names){auto& t=w.tensors.at(name);uint32_t len=name.size(),rank=t.shape.size();
    std::fwrite(&len,4,1,f);std::fwrite(name.data(),1,len,f);std::fwrite(&t.dtype,1,1,f);std::fwrite(&rank,4,1,f);
    std::fwrite(t.shape.data(),4,rank,f);std::fwrite(t.data.data(),1,t.data.size(),f);}
  if(std::ferror(f)){std::fclose(f);return 6;}std::fclose(f);
  return 0;
}
