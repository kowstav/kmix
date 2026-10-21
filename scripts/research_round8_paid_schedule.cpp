#include "research_round8_conditional_library.h"
struct PolicyProgram8 { double net=0;vector<array<int,3>>segments; };
double idbits8(int c,int k){return c==0?1:log2(2.*(k-1));}
int gammabits8(int n){int l=0;for(int v=n;v>1;v>>=1)l++;return 1+2*l;}
PolicyProgram8 optimize8(const vector<vector<double>>&sum,const vector<int>&options){
 int B=sum.size()-1,K=options.size();vector<double>d(B+1,-1e300);vector<int>from(B+1),choice(B+1);d[0]=0;
 for(int j=1;j<=B;j++)for(int i=0;i<j;i++){
  double best=-1e300;int chosen=0;for(int c=0;c<K;c++){int option=options[c];double a=sum[j][option]-sum[i][option]-idbits8(c,K);if(a>best){best=a;chosen=c;}}
  double score=d[i]+best-gammabits8(j-i);if(score>d[j]){d[j]=score;from[j]=i;choice[j]=chosen;}
 }
 PolicyProgram8 p;p.net=d[B];int j=B;while(j){int i=from[j];p.segments.push_back({i,j,options[choice[j]]});j=i;}reverse(p.segments.begin(),p.segments.end());
 return p;
}
void program_json8(ostream&f,const PolicyProgram8&p,const string&name,int K){f<<"{\"name\":\""<<name<<"\",\"options\":"<<K<<",\"program_net_gain_bits\":"<<p.net<<",\"saving_bytes_including_mode\":"<<(max(0.,p.net)-1)/8<<",\"mode\":\""<<(p.net>0?"PAID_PROGRAM":"IDENTITY")<<"\",\"segments\":[";for(size_t i=0;i<p.segments.size();i++){if(i)f<<',';auto s=p.segments[i];f<<'['<<s[0]<<','<<s[1]<<','<<s[2]<<']';}f<<"]}";}
void dp_trace8(){int B,K;cin>>B>>K;vector<vector<double>>sum(B+1,vector<double>(K));for(int i=1;i<=B;i++)for(int c=0;c<K;c++){double g;cin>>g;sum[i][c]=sum[i-1][c]+g;}vector<int>ids(K);iota(ids.begin(),ids.end(),0);auto p=optimize8(sum,ids);cout<<setprecision(17);program_json8(cout,p,"selftest",K);cout<<'\n';}
void run_schedule8(string rp,string pp,string dict,string graph,string constructors,size_t limit,string out){
 auto start=chrono::steady_clock::now();FastExpert8 x(dict,graph,constructors);string raw=readfile(rp),ps=readfile(pp);if(ps.size()!=raw.size()*16)throw runtime_error("trace/input size mismatch");if(limit&&limit<raw.size())raw.resize(limit);
 size_t found=raw.find(marker8(x));if(found==string::npos)throw runtime_error("no synchronization");size_t offset=found+marker8(x).size();x.page_start();
 constexpr int U=1024,C=97;int B=(raw.size()+U-1)/U;vector<vector<double>>sum(B+1,vector<double>(C));int node=0;bool escape=false,upper=false,capital=false;vector<int>code;double atomcost=0,baseline=0;uint64_t bits=0;
 for(size_t i=offset;i<raw.size();i++){
  if(code.empty()&&!escape)x.prepare_fast();
  for(int j=0;j<8;j++){
   int p=(unsigned char)ps[16*i+2*j]|((unsigned char)ps[16*i+2*j+1]<<8);if(!p)throw runtime_error("invalid p");int y=((unsigned char)raw[i]>>(7-j))&1;auto d=x.deltas(node);double l=log(double(p)/(65536-p));
   array<pair<double,double>,4>sig={pair<double,double>{1.,clamp(l,-8.,8.)},{d[3],d[8]},{d[7],d[8]},{d[4],d[8]}};double native=y?p:65536-p;double cost=-log2(native/65536.);atomcost+=cost;baseline+=cost;
   for(int a=0;a<4;a++){auto q=candidates8(p,sig[a].first,sig[a].second);if(q[0]!=p)throw runtime_error("nonidentity candidate");for(int k=1;k<K8;k++)sum[i/U+1][1+a*24+k-1]+=log2(double(y?q[k]:65536-q[k])/native);}bits++;if(node>=0)node=x.tr[node].c[y];
  }
  int c=inv((unsigned char)raw[i]);if(escape){x.chars(string(1,char(c)),atomcost);escape=false;node=0;atomcost=0;}
  else if(code.empty()&&c==12){escape=true;node=-1;}
  else if(code.empty()&&c<128){if(c==7)upper=true;else if(c==64)capital=true;else if(c==6)upper=false;else{if(!(c>=65&&c<=90)&&!(c>=97&&c<=122))upper=false;if(capital||upper)c=(c-32)&255;capital=false;x.chars(string(1,char(c)),atomcost);}node=0;atomcost=0;}
  else{code.push_back(c);bool done=code.size()==1?c<=207:code.size()==2?c<=207:true;if(done){if(node<0||x.tr[node].leaf<0)throw runtime_error("WRT parse");string s=x.w[x.tr[node].leaf];if(capital){s[0]-=32;capital=false;}if(upper)for(char&a:s)if(a>='a'&&a<='z')a-=32;x.chars(s,atomcost);code.clear();node=0;atomcost=0;}}
 }
 if(bits!=8*(raw.size()-offset))throw runtime_error("bit accounting");for(int i=1;i<=B;i++)for(int c=0;c<C;c++)sum[i][c]+=sum[i-1][c];
 ofstream f(out);f<<setprecision(17)<<"{\"raw_bytes\":"<<raw.size()<<",\"synchronization_offset\":"<<offset<<",\"scored_bits\":"<<bits<<",\"baseline_scored_bytes\":"<<baseline/8<<",\"unit_bytes\":"<<U<<",\"units\":"<<B<<",\"programs\":[";
 for(int a=0;a<5;a++){if(a)f<<',';vector<int>opts={0};if(a<4)for(int k=1;k<K8;k++)opts.push_back(1+a*24+k-1);else for(int c=1;c<C;c++)opts.push_back(c);auto p=optimize8(sum,opts);program_json8(f,p,a<4?ARM8[a]:"combined",opts.size());}
 f<<"],\"fixed_candidates_gain_bytes\":[";for(int c=0;c<C;c++){if(c)f<<',';f<<sum[B][c]/8;}f<<"],\"wall_seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<",\"status\":\"PRICED_POLICY_PROGRAM_REPLAY_NOT_ARCHIVE\",\"core_retraining\":false,\"all_pre_sync_predictions_identity\":true,\"deletions\":[]}";
}
int main(int argc,char**argv){try{if(argc==2&&string(argv[1])=="dp_trace"){dp_trace8();return 0;}if(argc!=8)return 2;run_schedule8(argv[1],argv[2],argv[3],argv[4],argv[5],stoull(argv[6]),argv[7]);return 0;}catch(exception&e){cerr<<e.what()<<'\n';return 1;}}
