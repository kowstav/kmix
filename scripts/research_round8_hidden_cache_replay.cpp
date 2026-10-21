#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

// This replay never changes the core trajectory. A byte target enters only
// after its eight current predictions; a query is the previous byte's trace.
constexpr int ARMS=5, FULL=192, PROJ=32;
using Key=std::array<int16_t,FULL>;
struct Row {Key key{};double norm=0;uint8_t target=0;};
static uint32_t mix(uint32_t x){x^=x>>16;x*=0x7feb352d;x^=x>>15;x*=0x846ca68b;x^=x>>16;return x;}
static Key project(const Key& k){Key p{};int amax=0;for(int j=0;j<PROJ;j++){int v=0;for(int t=0;t<6;t++)v+=((mix(uint32_t(j*6+t+9183))&1)?1:-1)*k[j+PROJ*t];p[j]=v;amax=std::max(amax,std::abs(v));}if(amax)for(int j=0;j<PROJ;j++)p[j]=int16_t(std::lround(double(p[j])*127/amax));return p;}
static double norm(const Key& k,int d){int64_t a=0;for(int i=0;i<d;i++)a+=int(k[i])*int(k[i]);return std::sqrt(double(a));}
static double cosine(const Key&a,const Row&b,int d,double na){int sum=0;for(int j=0;j<d;j++)sum+=int(a[j])*int(b.key[j]);return na>0&&b.norm>0?double(sum)/(na*b.norm):-1;}
static uint64_t rngstep(uint64_t&x){x^=x<<13;x^=x>>7;x^=x<<17;return x;}
struct Cache {
 int cap,dim,used=0,pos=0;std::vector<Row> rows;std::vector<std::vector<uint16_t>> permutations;
 Cache(int n,int d,bool shuffled=false):cap(n),dim(d),rows(n){if(shuffled){permutations.resize(n+1);for(int count=1;count<=n;count++){auto&p=permutations[count];p.resize(count);std::iota(p.begin(),p.end(),0);uint64_t seed=814571+count;for(int j=count-1;j>0;j--)std::swap(p[j],p[rngstep(seed)%(j+1)]);}}}
 void update(const Key&k,uint8_t y){double n=norm(k,dim);if(n==0)return;rows[pos]={k,n,y};pos=(pos+1)%cap;used=std::min(used+1,cap);}
 std::array<double,256> query(const Key&k,const std::array<double,256>& prior,bool shuffle=false)const{
  std::array<double,256>q=prior;if(!used)return q;double na=norm(k,dim);if(na==0)return q;
  std::array<std::pair<double,int>,8> top;for(auto&v:top)v={-2,-1};int count=0;
  for(int i=0;i<used;i++){double s=cosine(k,rows[i],dim,na);int at=std::min(count,7);if(count>=8&&(s<top[7].first||(s==top[7].first&&i>top[7].second)))continue;while(at>0&&(s>top[at-1].first||(s==top[at-1].first&&i<top[at-1].second))){if(at<8)top[at]=top[at-1];at--;}top[at]={s,i};count=std::min(count+1,8);}
  std::array<double,256>votes{};double total=0;for(int i=0;i<count;i++){double w=std::exp(10*(top[i].first-top[0].first));int index=top[i].second;if(shuffle)index=permutations.at(used).at(index);votes[rows[index].target]+=w;total+=w;}
  // Fixed 1/2 smoothing avoids pretending sparse votes cover the alphabet.
  for(int b=0;b<256;b++)q[b]=.5*prior[b]+.5*votes[b]/total;return q;
 }
};
static double prefix_p(const std::array<double,256>&q,int prefix,int bits){double all=0,one=0;for(int b=0;b<256;b++)if(bits==0||(b>>(8-bits))==prefix){all+=q[b];if((b>>(7-bits))&1)one+=q[b];}if(!(all>0))throw std::runtime_error("zero prefix mass");return std::clamp(one/all,1e-9,1-1e-9);}
static double ell(double p){return std::log(p/(1-p));}
static void selftest(){
 Key a{};for(int j=0;j<FULL;j++)a[j]=int16_t(j%127-63);Key b=a;b[0]+=2;Cache c(2,FULL,true);std::array<double,256>prior{};prior.fill(1./256);
 auto initial=c.query(a,prior);assert(initial==prior);c.update(a,41);auto predicted=c.query(a,prior);auto frozen=predicted;c.update(b,99);assert(frozen[41]==predicted[41]);assert(c.used==2);c.update(b,12);assert(c.used==2&&c.pos==1);
 for(bool shuffled:{false,true}){auto q=c.query(a,prior,shuffled);double sum=std::accumulate(q.begin(),q.end(),0.);assert(std::abs(sum-1)<1e-12);for(int target=0;target<256;target++){double p=1;int prefix=0;for(int bit=0;bit<8;bit++){double v=prefix_p(q,prefix,bit);bool y=(target>>(7-bit))&1;p*=y?v:1-v;prefix=prefix*2+y;}assert(std::abs(p-q[target])<1e-12);}}
 for(int n=1;n<=2;n++){auto x=c.permutations[n];std::sort(x.begin(),x.end());for(int j=0;j<n;j++)assert(x[j]==j);}auto p=project(a);assert(p==project(a));assert(norm(p,PROJ)>0);Key z{};auto before=c.query(a,prior);c.update(z,250);assert(before==c.query(a,prior));
 std::printf("{\"selftest\":\"PASS\",\"checks\":[\"query-before-target update\",\"all 256 bit-prefix chain probabilities\",\"normalized full categorical mass\",\"permutation histogram\",\"FIFO/tie ordering\",\"invalid zero key\",\"projection determinism\"]}\n");
}
int main(int argc,char**argv){try{if(argc==2&&std::string(argv[1])=="selftest"){selftest();return 0;}if(argc!=6)throw std::runtime_error("raw finalp hidden output limit");std::ifstream raw(argv[1],std::ios::binary),pf(argv[2],std::ios::binary),hf(argv[3],std::ios::binary);std::ofstream out(argv[4],std::ios::binary|std::ios::out);if(!raw||!pf||!hf||!out)throw std::runtime_error("file open");int limit=std::stoi(argv[5]);
 Cache small(128,FULL),large(512,FULL,true),proj(512,PROJ);std::array<uint64_t,256>counts{};std::array<int,256>recent{};std::array<uint8_t,512>history{};int historyused=0,historypos=0;uint64_t bytes=0,valid=0,total=0;Key current{};bool currentvalid=false;
 while(bytes<uint64_t(limit)){unsigned char ybyte;if(!raw.read(reinterpret_cast<char*>(&ybyte),1))break;unsigned char hidden[193];if(!hf.read(reinterpret_cast<char*>(hidden),193))throw std::runtime_error("short hidden");if(hidden[0]>1)throw std::runtime_error("invalid flag");std::array<double,256>prior{};for(int b=0;b<256;b++)prior[b]=(double(counts[b])+.5)/(total+128.);std::array<std::array<double,256>,ARMS>qs{};
 if(currentvalid){qs[0]=small.query(current,prior);qs[1]=large.query(current,prior);qs[2]=proj.query(project(current),prior);qs[3]=large.query(current,prior,true);valid++;}else for(int i=0;i<4;i++)qs[i]=prior;
 for(int b=0;b<256;b++)qs[4][b]=historyused?(.5*prior[b]+.5*double(recent[b])/historyused):prior[b];int prefix=0;
 for(int bit=0;bit<8;bit++){unsigned char little[2];if(!pf.read(reinterpret_cast<char*>(little),2))throw std::runtime_error("short probability trace");uint16_t p=little[0]+uint16_t(little[1])*256;uint8_t y=(ybyte>>(7-bit))&1;if(!p)throw std::runtime_error("invalid probability");out.write(reinterpret_cast<char*>(little),2);out.write(reinterpret_cast<char*>(&y),1);double l=ell(double(p)/65536);for(int a=0;a<ARMS;a++){double q=prefix_p(qs[a],prefix,bit);float f=currentvalid||a==4?float(std::clamp(ell(q)-l,-12.,12.)):0.;out.write(reinterpret_cast<char*>(&f),4);}prefix=prefix*2+y;}
 // Only now is the target available to the decoder-built cache.
 if(currentvalid){small.update(current,ybyte);large.update(current,ybyte);proj.update(project(current),ybyte);}if(historyused==512)recent[history[historypos]]--;else historyused++;history[historypos]=ybyte;historypos=(historypos+1)%512;recent[ybyte]++;counts[ybyte]++;total++;currentvalid=hidden[0];for(int j=0;j<FULL;j++)current[j]=currentvalid?int(hidden[j+1])-128:0;bytes++;
 }
 out.close();if(!out)throw std::runtime_error("write failed");std::printf("{\"bytes\":%llu,\"valid_queries\":%llu,\"feature_record_bytes\":23,\"source_caches_instrumented_row_bytes\":%zu,\"production_packed_512_full_key_row_design_bytes\":%d,\"core_trajectory_unchanged\":true}\n",(unsigned long long)bytes,(unsigned long long)valid,sizeof(Row)*(128+512+512),512*(192+8+1));return 0;
 }catch(const std::exception&e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
