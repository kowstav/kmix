#define main previous_atom_main
#include "research_round8_atom_cache.cpp"
#undef main
#include <iomanip>
#include <set>
#include <sstream>
constexpr int RP=27;
struct Sum{double v=0,c=0;Sum&operator+=(double x){double y=x-c,t=v+y;c=(t-v)-y;v=t;return *this;}Sum&operator-=(double x){return *this+=-x;}operator double()const{return v;}};
struct RCell{double beta=0,h=0;};
struct RPolicy{vector<RCell>cell;double lambda,eta;Sum loss;uint64_t hash=1469598103934665603ULL;int family;
 RPolicy(int f,double l,double e):cell(f?3840:256),lambda(l),eta(e),family(f){for(auto&c:cell)c.h=l;}
 int query(int z,int p,double&ideal)const{ideal=logistic(ell(double(p)/65536.)+cell[z].beta);return quant(ideal);}
 void observe(int z,int q,int y,double ideal){auto&c=cell[z];c.h+=ideal*(1-ideal);c.beta=clamp(c.beta+eta*(y-ideal)/c.h,-1.,1.);loss-=log2(double(y?q:65536-q)/65536.);hash^=q;hash*=1099511628211ULL;}
};
void rtest(){for(int p=1;p<65536;p++)if(quant(logistic(ell(double(p)/65536.)))!=p)throw runtime_error("all-integer identity");RPolicy a(0,16,1);double ideal;int q=a.query(0,32768,ideal);if(q!=32768)throw runtime_error("zero state");a.observe(0,q,1,ideal);if(abs(a.cell[0].beta-.5/16.25)>1e-15)throw runtime_error("independent toy update");if(gcd(293,44515)!=1)throw runtime_error("permutation not bijective");printf("{\"status\":\"PASS\",\"all_65535_native_identity\":true,\"independent_toy_update\":true,\"vocabulary_permutation_bijection\":true}\n");}
int main(int argc,char**argv){try{
 if(argc==2&&string(argv[1])=="selftest"){rtest();return 0;}if(argc!=6&&argc!=7)throw runtime_error("raw p dictionary result byte_limit [prefix_trace]");string raw=file(argv[1]),prob=file(argv[2]);size_t size=stoull(argv[5]);raw.resize(min(raw.size(),size));if(prob.size()<16*raw.size())throw runtime_error("probabilities short");ofstream trace;if(argc==7)trace.open(argv[6],ios::binary);Codes c(argv[3]);size_t found=raw.find(c.marker);if(found==string::npos)throw runtime_error("marker missing");size_t start=found+c.marker.size();vector<int>role(c.code.size(),3);string dictionary=file(argv[3]);regex rx("[a-z]+");set<string>constructors;istringstream is("the a an is are was were be been being and or but if then as at by for from in of on to with that which who whom whose this these those it its he she they we you i not no now there here when where how what why do does did have has had can could shall should will would may might must than so all any some such also into over under between through after before during");string w;while(is>>w)constructors.insert(w);int j=0;for(sregex_iterator it(dictionary.begin(),dictionary.end(),rx),end;it!=end;++it,++j){auto code=wordcode(j);uint32_t padded=0;for(int z=0;z<int(code.size());z++)padded|=uint32_t(code[z])<<(16-8*z);role[c.rank(padded)]=constructors.count(it->str())?1:2;}vector<uint32_t>().swap(c.tree);
 vector<RPolicy>policies;for(int family=0;family<3;family++)for(double lambda:{1.,16.,256.})for(double eta:{.25,1.,4.})policies.emplace_back(family,lambda,eta);array<double,RP+1>logw;array<Sum,RP+1>component_losses{};logw.fill(log(.5/RP));logw[0]=log(.5);Sum base,mix,ideal_mix;uint64_t mixed_hash=1469598103934665603ULL;int prev=0,nullprev=0,depth=0,bits=0;uint32_t prefix=0;bool escape=false;
 for(size_t i=0;i<raw.size();i++){uint8_t byte=uint8_t(raw[i]);for(int b=0;b<8;b++){
  int p=uint8_t(prob[16*i+2*b])+(int(uint8_t(prob[16*i+2*b+1]))<<8);if(!p)throw runtime_error("zero native p");array<int,RP+1>q{};array<double,RP>ideals{};q[0]=p;int bucket=min(31,p/2048),generic=b*32+bucket,actual=((prev*3+min(depth,2))*8+b)*32+bucket,control=((nullprev*3+min(depth,2))*8+b)*32+bucket;
  for(int k=0;k<RP;k++){int z=policies[k].family==0?generic:policies[k].family==1?actual:control;q[k+1]=policies[k].query(z,p,ideals[k]);}
  double mx=*max_element(logw.begin(),logw.end()),normalizer=0,pred=0;for(int k=0;k<=RP;k++){double v=exp(logw[k]-mx);normalizer+=v;pred+=v*q[k];}pred/=normalizer*65536.;int mixed=quant(pred);mixed_hash^=mixed;mixed_hash*=1099511628211ULL;if(argc==7&&i<4096){for(int v:q){uint16_t u=v;trace.write(reinterpret_cast<const char*>(&u),2);}uint16_t u=mixed;trace.write(reinterpret_cast<const char*>(&u),2);}
  // All forecasts and context choices precede consumption of the target.
  int y=(byte>>(7-b))&1;double bc=-log2(double(y?p:65536-p)/65536.);base+=bc;mix-=log2(double(y?mixed:65536-mixed)/65536.);ideal_mix-=log2(y?pred:1-pred);
  for(int k=0;k<=RP;k++){double loss=-log(double(y?q[k]:65536-q[k])/65536.);logw[k]-=loss;component_losses[k]+=loss;}
  // Removing a common log normalizer cannot destroy a recovering component.
  double wm=*max_element(logw.begin(),logw.end());for(auto&v:logw)v-=wm;
  for(int k=0;k<RP;k++){int z=policies[k].family==0?generic:policies[k].family==1?actual:control;policies[k].observe(z,q[k+1],y,ideals[k]);}
  if(i>=start&&!escape){prefix=prefix*2+y;bits++;}
 }
 if(i<start)continue;if(escape){escape=false;prev=nullprev=4;continue;}int original=inv(byte);depth++;if(original<208||depth==3){int rank=c.rank(prefix<<(24-bits));prev=role[rank];nullprev=rank<128?3:role[128+((rank-128)*293+17)%44515];escape=depth==1&&original==12;depth=bits=0;prefix=0;}
 }
 array<double,RP+1>batch{};for(int k=0;k<=RP;k++)batch[k]=log(k==0?.5:.5/RP)-component_losses[k];double bm=*max_element(batch.begin(),batch.end()),bz=0;for(double v:batch)bz+=exp(v-bm);double closed=-(bm+log(bz))/log(2);if(abs(closed-ideal_mix)>1e-5||base-closed<-1.00000001)throw runtime_error("independent batch normalizer/regret");ofstream out(argv[4]);out<<setprecision(17)<<"{\"bytes\":"<<raw.size()<<",\"baseline_likelihood_bytes\":"<<base/8<<",\"mixture_Q16_saving_bytes\":"<<(base-mix)/8<<",\"mixture_ideal_saving_bytes\":"<<(base-ideal_mix)/8<<",\"batch_mixture_ideal_saving_bytes\":"<<(base-closed)/8<<",\"batch_normalizer_bits_error\":"<<ideal_mix-closed<<",\"mixture_hash\":\""<<mixed_hash<<"\",\"production_single_role_bank_nominal_bytes\":61440,\"unscored_parser_prefix\":"<<start<<",\"results\":[";
 for(int k=0;k<RP;k++){auto&a=policies[k];if(k)out<<',';out<<"{\"policy\":"<<k<<",\"family\":"<<a.family<<",\"lambda\":"<<a.lambda<<",\"eta\":"<<a.eta<<",\"Q16_saving_bytes\":"<<(base-a.loss)/8<<",\"prediction_hash\":\""<<a.hash<<"\"}";}out<<"],\"core_unchanged\":true}";return 0;
 }catch(const exception&e){fprintf(stderr,"%s\n",e.what());return 1;}}
