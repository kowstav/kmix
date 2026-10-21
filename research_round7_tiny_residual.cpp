// I10 bounded alternate arm: 128 shared final-bit calibration offsets.
// Fits only A/B; C/D frozen. Native inference uses integer rational odds.
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
string read(string p){ifstream f(p,ios::binary);if(!f)throw runtime_error("missing "+p);return string(istreambuf_iterator<char>(f),{});}
int adjust(int p,uint32_t factor){uint64_t a=uint64_t(p)*factor,b=uint64_t(65536-p)*(1u<<20),den=a+b;return clamp(int((a*65536+den/2)/den),1,65535);}
struct Counts{vector<uint32_t>n,y;Counts():n(8*65536),y(8*65536){}void observe(string raw,string ps){assert(ps.size()==raw.size()*16);for(size_t i=0;i<raw.size();i++)for(int j=0;j<8;j++){int p=(unsigned char)ps[16*i+2*j]|int((unsigned char)ps[16*i+2*j+1])<<8;assert(p);int k=j*65536+p;n[k]++;y[k]+=((unsigned char)raw[i]>>(7-j))&1;}}};
array<uint32_t,128>fit(Counts&c,double ridge){array<uint32_t,128>f;for(int j=0;j<8;j++)for(int bin=0;bin<16;bin++){double beta=0;for(int step=0;step<24;step++){double grad=ridge*beta,hess=ridge;for(int p=max(1,4096*bin);p<min(65536,4096*(bin+1));p++){int k=j*65536+p;if(!c.n[k])continue;double q=1./(1+exp(-(log(double(p)/(65536-p))+beta)));grad+=c.n[k]*q-c.y[k];hess+=c.n[k]*q*(1-q);}double next=clamp(beta-grad/hess,-.25,.25);if(abs(next-beta)<1e-12){beta=next;break;}beta=next;}f[j*16+bin]=uint32_t(floor(exp(beta)*(1u<<20)+.5));}return f;}
int main(int argc,char**argv){try{assert(argc==7);Counts c;c.observe(read(argv[1]),read(argv[2]));c.observe(read(argv[3]),read(argv[4]));string prefix=argv[5],outdir=argv[6];ofstream out(outdir+"/results.json");out.precision(17);out<<"{\"trained_on\":\"A/B only\",\"neural_weights_changed\":false,\"model_bytes_per_copy\":512,\"identity_integer_odds\":true,\"arms\":[";
 for(int p=1;p<65536;p++)assert(adjust(p,1u<<20)==p);
 for(int arm=0;arm<2;arm++){double ridge=arm?4096:64;auto f=fit(c,ridge);ofstream mf(outdir+"/odds_"+to_string(arm)+".u32",ios::binary);for(uint32_t v:f)for(int j=0;j<4;j++)mf.put(char(v>>(8*j)));if(arm)out<<',';out<<"{\"ridge\":"<<ridge<<",\"model\":\"odds_"<<arm<<".u32\",\"slices\":[";
  for(int s=0;s<4;s++){char name='a'+s;string raw=read(prefix+"/"+name+"2m.bin"),ps=read(prefix+"/"+name+"_p.u16");assert(ps.size()==raw.size()*16);double gain=0,base=0;uint64_t changed=0;for(size_t i=0;i<raw.size();i++)for(int j=0;j<8;j++){int p=(unsigned char)ps[16*i+2*j]|int((unsigned char)ps[16*i+2*j+1])<<8;int q=adjust(p,f[j*16+(p>>12)]);bool y=((unsigned char)raw[i]>>(7-j))&1;double old=y?p:65536-p,newp=y?q:65536-q;gain+=log2(newp/old);base-=log2(old/65536.);changed+=p!=q;}if(s)out<<',';out<<"{\"slice\":\""<<name<<"\",\"role\":\""<<(s<2?"training":"confirmation")<<"\",\"raw_bytes\":"<<raw.size()<<",\"scored_bits\":"<<raw.size()*8<<",\"saving_bytes\":"<<gain/8<<",\"baseline_bytes\":"<<base/8<<",\"changed_bits\":"<<changed<<'}';}
  out<<"]}";
 }out<<"],\"contract\":\"every actual final uint16 bit; fixed128 integer odds factors; paid512B per model copy; no original transformer SGD; C/D previously examined regions, freshE/F required for promotion\"}";return 0;
 }catch(exception&e){cerr<<e.what()<<'\n';return 1;}}
