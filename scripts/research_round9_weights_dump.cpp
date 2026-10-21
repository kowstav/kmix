#include "weights_io.h"
#include <cstdio>
#include <string>
#include <algorithm>
int main(int argc,char**argv){if(argc!=3)return 10;auto w=fx2::WeightsFile::load_compressed(argv[1]);FILE*f=fopen(argv[2],"wb");if(!f)return 11;fwrite("FX2TFW01",1,8,f);uint32_t n=w.tensors.size();fwrite(&n,4,1,f);std::vector<std::string>names;for(auto&p:w.tensors)names.push_back(p.first);std::sort(names.begin(),names.end());for(auto&name:names){auto&t=w.tensors.at(name);uint32_t l=name.size(),d=t.shape.size();fwrite(&l,4,1,f);fwrite(name.data(),1,l,f);fwrite(&t.dtype,1,1,f);fwrite(&d,4,1,f);fwrite(t.shape.data(),4,d,f);fwrite(t.data.data(),1,t.data.size(),f);}fclose(f);return 0;}
