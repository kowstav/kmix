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
constexpr int ARMS=7, FULL=192, PROJ=32;
using Key=std::array<int16_t,FULL>;
struct Row {Key key{};double norm=0;uint8_t target=0;};
static uint32_t mix(uint32_t x){x^=x>>16;x*=0x7feb352d;x^=x>>15;x*=0x846ca68b;x^=x>>16;return x;}
static Key project(const Key& k){Key p{};int amax=0;for(int j=0;j<PROJ;j++){int v=0;for(int t=0;t<6;t++)v+=((mix(uint32_t(j*6+t+9183))&1)?1:-1)*k[j+PROJ*t];p[j]=v;amax=std::max(amax,std::abs(v));}if(amax)for(int j=0;j<PROJ;j++)p[j]=int16_t(std::lround(double(p[j])*127/amax));return p;}
static double norm(const Key& k,int d){int64_t a=0;for(int i=0;i<d;i++)a+=int(k[i])*int(k[i]);return std::sqrt(double(a));}
static double cosine(const Key&a,const Row&b,int d,double na){int sum=0;for(int j=0;j<d;j++)sum+=int(a[j])*int(b.key[j]);return na>0&&b.norm>0?double(sum)/(na*b.norm):-1;}
static uint64_t rngstep(uint64_t&x){x^=x<<13;x^=x>>7;x^=x<<17;return x;}
struct Cache {
 int cap,dim,used=0,pos=0;bool reservoir=false;uint64_t seen=0,randomstate=918741;std::vector<Row> rows;std::vector<std::vector<uint16_t>> permutations;
 Cache(int n,int d,bool shuffled=false,bool keep_old=false):cap(n),dim(d),reservoir(keep_old),rows(n){if(shuffled){permutations.resize(n+1);for(int count=1;count<=n;count++){auto&p=permutations[count];p.resize(count);std::iota(p.begin(),p.end(),0);uint64_t seed=814571+count;for(int j=count-1;j>0;j--)std::swap(p[j],p[rngstep(seed)%(j+1)]);}}}
 void update(const Key&k,uint8_t y){double n=norm(k,dim);if(n==0)return;seen++;if(reservoir){if(used<cap){rows[used++]={k,n,y};return;}uint64_t pick=rngstep(randomstate)%seen;if(pick<uint64_t(cap))rows[pick]={k,n,y};return;}rows[pos]={k,n,y};pos=(pos+1)%cap;used=std::min(used+1,cap);}
 std::array<double,256> query(const Key&k,const std::array<double,256>& prior,bool shuffle=false,double* best_similarity=nullptr)const{
  std::array<double,256>q=prior;if(best_similarity)*best_similarity=-1;if(!used)return q;double na=norm(k,dim);if(na==0)return q;
  std::array<std::pair<double,int>,8> top;for(auto&v:top)v={-2,-1};int count=0;
  for(int i=0;i<used;i++){double s=cosine(k,rows[i],dim,na);int at=std::min(count,7);if(count>=8&&(s<top[7].first||(s==top[7].first&&i>top[7].second)))continue;while(at>0&&(s>top[at-1].first||(s==top[at-1].first&&i<top[at-1].second))){if(at<8)top[at]=top[at-1];at--;}top[at]={s,i};count=std::min(count+1,8);}
  if(best_similarity)*best_similarity=top[0].first;std::array<double,256>votes{};double total=0;for(int i=0;i<count;i++){double w=std::exp(10*(top[i].first-top[0].first));int index=top[i].second;if(shuffle)index=permutations.at(used).at(index);votes[rows[index].target]+=w;total+=w;}
  // Fixed 1/2 smoothing avoids pretending sparse votes cover the alphabet.
  for(int b=0;b<256;b++)q[b]=.5*prior[b]+.5*votes[b]/total;return q;
 }
};
static double prefix_p(const std::array<double,256>&q,int prefix,int bits){double all=0,one=0;for(int b=0;b<256;b++)if(bits==0||(b>>(8-bits))==prefix){all+=q[b];if((b>>(7-bits))&1)one+=q[b];}if(!(all>0))throw std::runtime_error("zero prefix mass");return std::clamp(one/all,1e-9,1-1e-9);}
static double ell(double p){return std::log(p/(1-p));}
static void selftest(){
 Key a{};for(int j=0;j<FULL;j++)a[j]=int16_t(j%127-63);Key b=a;b[0]+=2;Cache c(2,FULL,true);std::array<double,256>prior{};prior.fill(1./256);
 double confidence=-2;auto initial=c.query(a,prior,false,&confidence);assert(confidence==-1);assert(initial==prior);c.update(a,41);auto predicted=c.query(a,prior,false,&confidence);assert(std::abs(confidence-1)<1e-12);auto frozen=predicted;c.update(b,99);assert(frozen[41]==predicted[41]);assert(c.used==2);c.update(b,12);assert(c.used==2&&c.pos==1);
 for(bool shuffled:{false,true}){auto q=c.query(a,prior,shuffled);double sum=std::accumulate(q.begin(),q.end(),0.);assert(std::abs(sum-1)<1e-12);for(int target=0;target<256;target++){double p=1;int prefix=0;for(int bit=0;bit<8;bit++){double v=prefix_p(q,prefix,bit);bool y=(target>>(7-bit))&1;p*=y?v:1-v;prefix=prefix*2+y;}assert(std::abs(p-q[target])<1e-12);}}
 for(int n=1;n<=2;n++){auto x=c.permutations[n];std::sort(x.begin(),x.end());for(int j=0;j<n;j++)assert(x[j]==j);}Cache rs(2,FULL,false,true),rs2(2,FULL,false,true);for(int i=0;i<100;i++){rs.update(a,uint8_t(i));rs2.update(a,uint8_t(i));}assert(rs.seen==100&&rs.used==2&&rs.rows[0].target==rs2.rows[0].target&&rs.rows[1].target==rs2.rows[1].target);auto p=project(a);assert(p==project(a));assert(norm(p,PROJ)>0);Key z{};auto before=c.query(a,prior);c.update(z,250);assert(before==c.query(a,prior));
 std::printf("{\"selftest\":\"PASS\",\"checks\":[\"query-before-target update\",\"all 256 bit-prefix chain probabilities\",\"normalized full categorical mass\",\"permutation histogram\",\"FIFO/tie ordering\",\"invalid zero key\",\"projection determinism\",\"long-term reservoir deterministic and bounded\"]}\n");
}

struct Stats {uint64_t n=0;std::array<double,FULL> mean{},m2{};void add(const Key&k){n++;for(int j=0;j<FULL;j++){double d=k[j]-mean[j];mean[j]+=d/n;m2[j]+=d*(k[j]-mean[j]);}}};
using Top=std::array<std::pair<double,int>,8>;
static Top retrieve(const Cache&c,const Key&k,const Stats&s,int metric){
 Top top;for(auto&v:top)v={-2,-1};int used=0;double qnorm=0;std::array<double,FULL>a{},w{},mu{};
 for(int j=0;j<FULL;j++){mu[j]=metric&&s.n>=16?s.mean[j]:0;w[j]=metric==2&&s.n>=16?1/(s.m2[j]/(s.n-1)+1):1;a[j]=k[j]-mu[j];qnorm+=a[j]*a[j]*w[j];}if(qnorm<1e-12)return top;
 for(int i=0;i<c.used;i++){double dot=0,rnorm=0;for(int j=0;j<FULL;j++){double b=c.rows[i].key[j]-mu[j];dot+=a[j]*b*w[j];rnorm+=b*b*w[j];}if(rnorm<1e-12)continue;double sim=std::clamp(dot/std::sqrt(qnorm*rnorm),-1.,1.);int at=std::min(used,7);if(used>=8&&(sim<top[7].first||(sim==top[7].first&&i>top[7].second)))continue;while(at>0&&(sim>top[at-1].first||(sim==top[at-1].first&&i<top[at-1].second))){if(at<8)top[at]=top[at-1];at--;}top[at]={sim,i};used=std::min(used+1,8);}return top;
}
struct Spec {int bank,metric,k;double tau,alpha;bool shuffled;};
const std::array<Spec,17> SPECS={{{0,0,8,10,.5,false},{0,0,1,1000,.99,false},{0,0,8,1000,.99,false},{0,0,8,100,.5,false},{0,1,1,1000,.99,false},{0,1,8,1000,.99,false},{0,2,1,1000,.99,false},{0,2,8,1000,.99,false},{0,0,1,1000,.99,true},{0,1,1,1000,.99,true},{0,2,1,1000,.99,true},{1,1,1,1000,.99,false},{1,1,8,1000,.99,false},{1,1,1,1000,.99,true},{1,2,1,1000,.99,false},{1,2,8,1000,.99,false},{1,2,1,1000,.99,true}}};
static std::array<double,256> law(const Cache&c,const Top&top,const Spec&sp,const std::array<double,256>&prior){
 if(top[0].second<0)return prior;std::array<double,256>q{},v{};double sum=0;for(int j=0;j<sp.k&&top[j].second>=0;j++){int i=top[j].second;if(sp.shuffled)i=c.permutations.at(c.used).at(i);double z=std::exp(sp.tau*(top[j].first-top[0].first));v[c.rows[i].target]+=z;sum+=z;}for(int b=0;b<256;b++)q[b]=(1-sp.alpha)*prior[b]+sp.alpha*v[b]/sum;return q;
}
static void metrictest(){selftest();Key a{},b{};for(int j=0;j<FULL;j++){a[j]=j%59-29;b[j]=j%41-20;}Cache c(3,FULL,true);c.update(a,61);c.update(b,77);Stats s;auto raw=retrieve(c,a,s,0);assert(raw[0].second==0&&std::abs(raw[0].first-1)<1e-12);assert(raw==retrieve(c,a,s,1));for(int i=0;i<50;i++)s.add(i&1?a:b);for(int m=0;m<3;m++){auto top=retrieve(c,a,s,m);assert(top[0].second==0&&std::abs(top[0].first-1)<1e-12);std::array<double,256>prior{};prior.fill(1./256);for(auto sp:SPECS){auto q=law(c,top,sp,prior);assert(std::abs(std::accumulate(q.begin(),q.end(),0.)-1)<1e-12);std::array<double,257>cdf{};for(int z=0;z<256;z++)cdf[z+1]=cdf[z]+q[z];for(int target=0;target<256;target++){int pre=0;double p=1;for(int j=0;j<8;j++){double v=prefix_p(q,pre,j);int low=pre<<(8-j),high=low+(1<<(8-j)),mid=(low+high)/2;double vc=(cdf[high]-cdf[mid])/(cdf[high]-cdf[low]);assert(std::abs(vc-v)<1e-10);int y=(target>>(7-j))&1;p*=y?v:1-v;pre=pre*2+y;}assert(std::abs(p-q[target])<1e-12);}}}std::printf("{\"metric_selftest\":\"PASS\",\"causal_center_whiten\":true,\"all_kernel_byte_prefix_laws\":true}\n");}
int main(int argc,char**argv){try{if(argc==2&&std::string(argv[1])=="selftest"){metrictest();return 0;}if(argc!=6)throw std::runtime_error("raw finalp hidden output limit");std::ifstream raw(argv[1],std::ios::binary),pf(argv[2],std::ios::binary),hf(argv[3],std::ios::binary);std::ofstream out(argv[4],std::ios::binary);if(!raw||!pf||!hf||!out)throw std::runtime_error("open failed");int limit=std::stoi(argv[5]);Cache normal(512,FULL,true),hard(512,FULL,true);Stats stats;Key current{};bool valid=false;std::array<uint64_t,256>count{};uint64_t n=0,queries=0,hardinserts=0;
 while(n<uint64_t(limit)){unsigned char target;if(!raw.read(reinterpret_cast<char*>(&target),1))break;unsigned char hidden[193];if(!hf.read(reinterpret_cast<char*>(hidden),193))throw std::runtime_error("short hidden");std::array<double,256>prior{};for(int b=0;b<256;b++)prior[b]=(count[b]+.5)/(n+128.);std::array<Top,6>tops;
 for(auto&t:tops)for(auto&v:t)v={-2,-1};if(valid){for(int m=0;m<3;m++){tops[m]=retrieve(normal,current,stats,m);tops[3+m]=retrieve(hard,current,stats,m);}queries++;}
 std::array<std::array<double,257>,17> cdf{};for(int a=0;a<17;a++){const auto&sp=SPECS[a];auto q=law(sp.bank?hard:normal,tops[sp.bank*3+sp.metric],sp,prior);for(int b=0;b<256;b++)cdf[a][b+1]=cdf[a][b]+q[b];}
 double bytecost=0;int prefix=0;
 for(int bit=0;bit<8;bit++){unsigned char le[2];if(!pf.read(reinterpret_cast<char*>(le),2))throw std::runtime_error("short probability trace");uint16_t p=le[0]+uint16_t(le[1])*256;if(!p)throw std::runtime_error("invalid p");uint8_t y=(target>>(7-bit))&1;out.write(reinterpret_cast<char*>(le),2);out.write(reinterpret_cast<char*>(&y),1);double l=ell(double(p)/65536);bytecost-=std::log2((y?p:65536-p)/65536.);int low=prefix<<(8-bit),high=low+(1<<(8-bit)),mid=(low+high)/2;
  for(int a=0;a<17;a++){double total=cdf[a][high]-cdf[a][low],one=cdf[a][high]-cdf[a][mid];double q=std::clamp(one/total,1e-9,1-1e-9);float f=valid?float(std::clamp(ell(q)-l,-12.,12.)):0;out.write(reinterpret_cast<char*>(&f),4);}prefix=prefix*2+y;
 }
 // Hard-memory retention uses observed loss only after the target completes.
 if(valid){normal.update(current,target);if(bytecost>2){hard.update(current,target);hardinserts++;}stats.add(current);}count[target]++;valid=hidden[0];for(int j=0;j<FULL;j++)current[j]=valid?int(hidden[j+1])-128:0;n++;
 }
 out.close();if(!out)throw std::runtime_error("output failed");std::printf("{\"bytes\":%llu,\"valid_queries\":%llu,\"hard_retained_events\":%llu,\"feature_record_bytes\":71,\"kernel_families\":17,\"metric_stats_bytes\":%zu}\n",(unsigned long long)n,(unsigned long long)queries,(unsigned long long)hardinserts,sizeof(stats));return 0;
}catch(const std::exception&e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
