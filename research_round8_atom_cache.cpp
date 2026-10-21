// Registered dictionary-atom residual experiment. Original coder is unchanged.
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <numeric>
#include <regex>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr int DIM=192, CAP=512, NS=9, K=41;
int inv(int c){if(c>=123&&c<127)c+=80-123;else if(c>=80&&c<84)c-=80-123;else if((c>=58&&c<=63)||(c>=74&&c<=79))c^=0x70;if(c==88||c==96)c^=88^96;return c;}
string file(const string&p){ifstream f(p,ios::binary);if(!f)throw runtime_error("input missing "+p);return string(istreambuf_iterator<char>(f),{});}
vector<uint8_t> wordcode(int j){vector<uint8_t> c;if(j<80)c={uint8_t(128+j)};else if(j<3920){j-=80;c={uint8_t(208+j/80),uint8_t(128+j%80)};}else{j-=3920;c={uint8_t(240+(j/80)/32),uint8_t(208+(j/80)%32),uint8_t(128+j%80)};}for(auto&a:c)a=inv(a);return c;}
struct Codes{
 vector<uint32_t> code,tree;uint32_t n=0;string marker;
 Codes(const string&dict){string d=file(dict);regex rx("[a-z]+");vector<string>w;for(sregex_iterator it(d.begin(),d.end(),rx),end;it!=end;++it)w.push_back(it->str());if(w.size()!=44515)throw runtime_error("dictionary count");
  for(int c=0;c<128;c++)code.push_back(uint32_t(inv(c))<<16);
  for(int j=0;j<int(w.size());j++){auto c=wordcode(j);uint32_t v=0;for(int i=0;i<int(c.size());i++)v|=uint32_t(c[i])<<(16-8*i);code.push_back(v);}
  sort(code.begin(),code.end());if(adjacent_find(code.begin(),code.end())!=code.end())throw runtime_error("code duplicate");tree.resize(code.size()+1);
  string text="  <page>\n    <title>";for(size_t i=0;i<text.size();){if(text[i]>='a'&&text[i]<='z'){size_t j=i;while(j<text.size()&&text[j]>='a'&&text[j]<='z')j++;auto it=find(w.begin(),w.end(),text.substr(i,j-i));if(it==w.end())throw runtime_error("marker word");for(auto c:wordcode(it-w.begin()))marker+=char(c);i=j;}else marker+=char(inv(uint8_t(text[i++])));}
 }
 pair<int,int> range(uint32_t prefix,int bits)const{if(bits<0||bits>24)throw runtime_error("prefix bits");uint32_t lo=prefix<<(24-bits),hi=lo+(1u<<(24-bits));return {lower_bound(code.begin(),code.end(),lo)-code.begin(),lower_bound(code.begin(),code.end(),hi)-code.begin()};}
 uint32_t sum(int i)const{uint32_t z=0;for(;i;i-=i&-i)z+=tree[i];return z;}
 double mass(pair<int,int> r)const{return (double(sum(r.second)-sum(r.first))+.5*(r.second-r.first))/(n+.5*code.size());}
 void add(int rank){if(rank<0||rank>=int(code.size()))throw runtime_error("target rank");for(int i=rank+1;i<int(tree.size());i+=i&-i)tree[i]++;n++;}
 int rank(uint32_t padded)const{auto it=lower_bound(code.begin(),code.end(),padded);if(it==code.end()||*it!=padded)throw runtime_error("WRT atom code absent");return it-code.begin();}
};
using Key=array<int16_t,DIM>;
struct Stats{
 uint64_t n=0;array<double,DIM>mu{},m2{};
 void add(const Key&k){n++;for(int j=0;j<DIM;j++){double d=k[j]-mu[j];mu[j]+=d/n;m2[j]+=d*(k[j]-mu[j]);}}
 double weight(int j,int mode)const{return mode==2?1/(m2[j]/max(uint64_t(1),n)+1):1;}
 double center(int j,int mode)const{return mode&&n>=16?mu[j]:0;}
 double cos(const Key&a,const Key&b,int mode)const{if(n<16)mode=0;double dot=0,aa=0,bb=0;for(int j=0;j<DIM;j++){double x=a[j]-center(j,mode),y=b[j]-center(j,mode),w=weight(j,mode);dot+=w*x*y;aa+=w*x*x;bb+=w*y*y;}if(aa<=0||bb<=0)return -2;return clamp(dot/sqrt(aa*bb),-1.,1.);}
};
struct Row{Key key{};uint16_t target=0;};
struct Donors{
 vector<pair<uint16_t,double>>a;
 double mass(pair<int,int> r)const{double z=0;for(auto[t,v]:a)if(t>=r.first&&t<r.second)z+=v;return z;}
};
struct Bank{
 array<Row,CAP>rows{};int used=0,pos=0;
 void add(const Key&k,int t){rows[pos]={k,uint16_t(t)};pos=(pos+1)%CAP;if(used<CAP)used++;}
 pair<Donors,Donors> query(const Key&key,const Stats&s,int mode)const{
  vector<pair<double,int>>v;v.reserve(used);for(int i=0;i<used;i++){double c=s.cos(key,rows[i].key,mode);if(c>-1.5)v.push_back({c,i});}auto less=[](auto a,auto b){return a.first>b.first||(a.first==b.first&&a.second<b.second);};int keep=min(8,int(v.size()));partial_sort(v.begin(),v.begin()+keep,v.end(),less);v.resize(keep);Donors actual,shuffle;if(v.empty())return {actual,shuffle};double z=0;for(auto[c,i]:v)z+=exp(1000*(c-v[0].first));for(auto[c,i]:v){double q=exp(1000*(c-v[0].first))/z;actual.a.push_back({rows[i].target,q});shuffle.a.push_back({rows[(i+17)%used].target,q});}return {actual,shuffle};
 }
};
int quant(double x){return clamp(int(floor(x*65536+.5)),1,65535);}
double ell(double x){return log(x/(1-x));}
double logistic(double x){if(x>=0)return 1/(1+exp(-x));double t=exp(x);return t/(1+t);}
struct Bayes{
 array<double,K>w{};double saving=0,ideal=0;uint64_t hash=1469598103934665603ULL,bits=0;
 Bayes(){w.fill(.5/(K-1));w[0]=.5;}
 void update(const array<int,K>&q,int y,int p){double pred=inner_product(w.begin(),w.end(),q.begin(),0.)/65536.;int pq=quant(pred);double base=double(y?p:65536-p)/65536.,lik=y?pred:1-pred;saving+=log2(double(y?pq:65536-pq)/65536./base);ideal+=log2(lik/base);hash^=pq;hash*=1099511628211ULL;for(int k=0;k<K;k++)w[k]*=double(y?q[k]:65536-q[k])/65536./lik;double z=accumulate(w.begin(),w.end(),0.);if(!(z>0&&isfinite(z)))throw runtime_error("posterior");for(auto&a:w)a/=z;bits++;}
};
array<int,K> candidates(int p,const array<float,NS>&sig){array<int,K>q{};q[0]=p;double l=ell(double(p)/65536.);q[1]=quant(logistic(l-.125));q[2]=quant(logistic(l+.125));q[3]=quant(logistic(.9*l));q[4]=quant(logistic(1.1*l));int i=5;for(double f:sig)for(double t:{-.125,.25,.5,1.})q[i++]=f==0?p:quant(logistic(l+t*f));if(i!=K)throw runtime_error("candidate count");return q;}
void selftest(const string&dict){Codes c(dict);if(c.code.size()!=44643)throw runtime_error("alphabet");for(int i=0;i<1000;i++)c.add((i*293)%c.code.size());for(int bits=0;bits<20;bits++){uint32_t p=bits?((1u<<bits)-1)/3:0;auto r=c.range(p,bits),a=c.range(p*2,bits+1),b=c.range(p*2+1,bits+1);if(abs(c.mass(r)-c.mass(a)-c.mass(b))>1e-13)throw runtime_error("prefix mass");double direct=0;for(int j=r.first;j<r.second;j++)direct+=double(c.sum(j+1)-c.sum(j))+.5;if(abs(c.mass(r)-direct/(c.n+.5*c.code.size()))>1e-13)throw runtime_error("independent prefix sum");}
 Key k{},z{};for(int j=0;j<DIM;j++){k[j]=(j*13)%127-63;z[j]=(j*31)%101-50;}Stats s;Bank bank;for(int i=0;i<40;i++){auto t=k;t[i%DIM]+=i;bank.add(t,i);s.add(t);}for(int mode=0;mode<3;mode++){auto d=bank.query(k,s,mode);for(auto*q:{&d.first,&d.second}){double mass=q->mass({0,int(c.code.size())});if(abs(mass-1)>1e-13)throw runtime_error("donor normalization");}if(s.cos(k,k,mode)<1-1e-12)throw runtime_error("same-coordinate identity");}vector<int>a,b;for(int i=0;i<bank.used;i++){a.push_back(bank.rows[i].target);b.push_back(bank.rows[(i+17)%bank.used].target);}sort(a.begin(),a.end());sort(b.begin(),b.end());if(a!=b)throw runtime_error("matched permutation histogram");auto before=bank.query(k,s,0);bank.add(z,41000);if(before.first.mass({0,40})<.999)throw runtime_error("query captured before insertion");
 Bayes g;array<float,NS>f{};for(int i=0;i<500;i++){int p=1+(i*7919)%65535;auto q=candidates(p,f);if(q[0]!=p)throw runtime_error("identity");g.update(q,i&1,p);}if(g.ideal<-.125000001)throw runtime_error("global mixture identity regret");printf("{\"status\":\"PASS\",\"prefix_interval_independent_sums\":true,\"all_child_masses_normalized\":true,\"same_coordinate_geometry\":true,\"permutation_target_histogram\":true,\"query_before_completed_target\":true,\"global_ideal_identity_regret_bound\":true,\"atoms\":44643}\n");
}
int main(int argc,char**argv){try{
 if(argc==3&&string(argv[1])=="selftest"){selftest(argv[2]);return 0;}if(argc!=8)throw runtime_error("raw finalp hidden dictionary output limit result");string raw=file(argv[1]),prob=file(argv[2]),hidden=file(argv[3]);size_t limit=stoull(argv[6]);if(limit<raw.size())raw.resize(limit);if(prob.size()<16*raw.size()||hidden.size()<193*raw.size())throw runtime_error("short native trace");Codes c(argv[4]);size_t find=raw.find(c.marker);if(find==string::npos)throw runtime_error("no sync marker");size_t offset=find+c.marker.size();ofstream out(argv[5],ios::binary);if(!out)throw runtime_error("output");
 Bank all,hard;Stats stats;array<Donors,NS>donors;vector<uint16_t>recent;Bayes global;array<Bayes,24>contexts;uint32_t prefix=0;int prefixbits=0,bytes_in_atom=0;bool escape=false,atomvalid=false;Key atomkey{};double atomcost=0;uint64_t atoms=0,words=0,valid=0,hardwords=0;double baseline=0;
 for(size_t i=0;i<raw.size();i++){
  bool active=i>=offset&&!escape;if(active&&bytes_in_atom==0){atomvalid=i>0&&uint8_t(hidden[193*(i-1)])==1;for(int j=0;j<DIM;j++)atomkey[j]=atomvalid?int(uint8_t(hidden[193*(i-1)+1+j]))-128:0;for(auto&d:donors)d.a.clear();if(atomvalid){for(int mode=0;mode<3;mode++){auto d=all.query(atomkey,stats,mode);donors[2*mode]=move(d.first);donors[2*mode+1]=move(d.second);}auto h=hard.query(atomkey,stats,1);donors[7]=move(h.first);donors[8]=move(h.second);valid++;}if(!recent.empty())for(auto rank:recent)donors[6].a.push_back({rank,1./recent.size()});prefix=0;prefixbits=0;atomcost=0;}
  uint8_t byte=uint8_t(raw[i]);for(int b=0;b<8;b++){
   uint16_t p=uint8_t(prob[16*i+2*b])+(uint16_t(uint8_t(prob[16*i+2*b+1]))<<8);if(!p)throw runtime_error("zero p");array<float,NS>f{};
   if(active){auto r0=c.range(prefix*2,prefixbits+1),r1=c.range(prefix*2+1,prefixbits+1);double g0=c.mass(r0),g1=c.mass(r1);if(g0>0&&g1>0){double logbase=log(g1/g0);for(int a=0;a<NS;a++)if(!donors[a].a.empty()){double q0=.1*g0+.9*donors[a].mass(r0),q1=.1*g1+.9*donors[a].mass(r1);f[a]=clamp(log(q1/q0)-logbase,-12.,12.);}}}
   // The current target bit is consumed only after all nine feature values.
   uint8_t y=(byte>>(7-b))&1;out.write(reinterpret_cast<char*>(&p),2);out.write(reinterpret_cast<char*>(&y),1);out.write(reinterpret_cast<char*>(f.data()),4*NS);auto q=candidates(p,f);global.update(q,y,p);contexts[b+8*min(bytes_in_atom,2)].update(q,y,p);double cost=-log2(double(y?p:65536-p)/65536.);baseline+=cost;if(active){atomcost+=cost;prefix=prefix*2+y;prefixbits++;}
  }
  if(i<offset)continue;if(escape){escape=false;continue;}int original=inv(byte);bytes_in_atom++;bool done=bytes_in_atom==1?original<208:bytes_in_atom==2?original<208:true;
  if(done){if(prefixbits!=8*bytes_in_atom)throw runtime_error("atom bit count");int target=c.rank(prefix<<(24-prefixbits));bool word=bytes_in_atom>1||original>=128;if(atomvalid){all.add(atomkey,target);if(word&&atomcost>2){hard.add(atomkey,target);hardwords++;}stats.add(atomkey);}c.add(target);if(word){recent.push_back(target);if(recent.size()>128)recent.erase(recent.begin());words++;}atoms++;escape=bytes_in_atom==1&&original==12;bytes_in_atom=0;prefix=0;prefixbits=0;}
 }
 out.close();if(!out)throw runtime_error("feature output failure");double cs=0,ci=0;for(auto&a:contexts){cs+=a.saving;ci+=a.ideal;}ofstream result(argv[7]);result.precision(17);result<<"{\"bytes\":"<<raw.size()<<",\"unscored_feature_prefix\":"<<offset<<",\"atoms\":"<<atoms<<",\"dictionary_atoms\":"<<words<<",\"valid_atom_queries\":"<<valid<<",\"admitted_hard_dictionary_atoms\":"<<hardwords<<",\"incomplete_atom_bytes_eof\":"<<bytes_in_atom<<",\"escape_eof\":"<<(escape?"true":"false")<<",\"baseline_likelihood_bytes\":"<<baseline/8<<",\"bayes_global_saving_bytes\":"<<global.saving/8<<",\"bayes_global_ideal_saving_bytes\":"<<global.ideal/8<<",\"bayes_global_prediction_hash\":\""<<global.hash<<"\",\"bayes_context_saving_bytes\":"<<cs/8<<",\"bayes_context_ideal_saving_bytes\":"<<ci/8<<",\"nominal_single_bank_code_and_counts_design_bytes\":"<<c.code.size()*8+CAP*(DIM+2+8)+3080<<",\"research_two_bank_rows_bytes\":"<<sizeof(all)+sizeof(hard)<<",\"feature_record_bytes\":39,\"original_core_unchanged\":true,\"status\":\"CANONICAL_COLD_REPLAY_NOT_ARCHIVE\"}";printf("{\"bytes\":%zu,\"atoms\":%llu,\"words\":%llu,\"global_bytes\":%.9f,\"context_bytes\":%.9f}\n",raw.size(),(unsigned long long)atoms,(unsigned long long)words,global.saving/8,cs/8);return 0;
 }catch(const exception&e){fprintf(stderr,"%s\n",e.what());return 1;}}
