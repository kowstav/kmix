// Frozen-core research replay, not a production archive. See registered protocol.
#define main old_remaining_replay_main
#include "research_round7_remaining_experts.cpp"
#undef main
#include <iomanip>
constexpr int K8=25, DEPTH8=6, MAXNODE8=20873;
const array<int,DEPTH8> RADIX8={8,8,5,4,3,4};
struct Posterior8 {
 array<double,K8> w{}, lw{};
 Posterior8(){w[0]=.5;lw[0]=log(.5);for(int k=1;k<K8;k++){w[k]=.5/(K8-1);lw[k]=log(w[k]);}}
 double predict(const array<int,K8>&q)const{double z=0;for(int k=0;k<K8;k++)z+=w[k]*q[k];return z/65536.;}
 void update(const array<double,K8>&lik,const array<double,K8>&ll,double local){
  double loglocal=log(local),z=0;
  for(int k=0;k<K8;k++){lw[k]+=ll[k]-loglocal;w[k]*=lik[k]/local;
   if(w[k]==0&&lw[k]>-700)w[k]=exp(lw[k]);z+=w[k];}
  if(!(z>0&&isfinite(z)))throw runtime_error("invalid posterior");
  double lz=log(z);for(int k=0;k<K8;k++){w[k]/=z;lw[k]-=lz;}
 }
};
struct GateNode8{array<int,8>child;Posterior8 p;double local_ll=0,split_ll=0,plocal=0,pmix=0;GateNode8(){child.fill(-1);}};
struct Gate8 {
 vector<GateNode8> nodes; array<int,DEPTH8+1> route{}; Posterior8 global;
 double saving=0,real_saving=0,global_saving=0,base=0;array<double,K8>fixed{};
 vector<double>interval;uint64_t bits=0,prediction_hash=1469598103934665603ULL;double max_weight_sum_error=0;
 Gate8(){nodes.reserve(MAXNODE8);nodes.emplace_back();}
 double predict(const array<int,K8>&q,const array<int,DEPTH8>&ctx){
  int v=0;route[0]=0;
  for(int d=0;d<DEPTH8;d++){int c=ctx[d];if(c<0||c>=RADIX8[d])throw runtime_error("context outside declared partition");
   if(nodes[v].child[c]<0){if(nodes.size()==MAXNODE8)throw runtime_error("declared tree size exceeded");int n=nodes.size();nodes.emplace_back();nodes[v].child[c]=n;}
   v=nodes[v].child[c];route[d+1]=v;}
  for(int d=DEPTH8;d>=0;d--){auto&n=nodes[route[d]];n.plocal=n.p.predict(q);
   if(d==DEPTH8)n.pmix=n.plocal;else{double delta=n.local_ll-n.split_ll;double stop=delta>=0?1./(1+exp(-delta)):exp(delta)/(1+exp(delta));n.pmix=stop*n.plocal+(1-stop)*nodes[route[d+1]].pmix;}
   if(!(n.pmix>0&&n.pmix<1&&isfinite(n.pmix)))throw runtime_error("invalid tree prediction");
  }return nodes[0].pmix;
 }
 void update(const array<int,K8>&q,int y,double baseprob,double pred){
  array<double,K8>lik,ll;for(int k=0;k<K8;k++){lik[k]=(y?q[k]:65536-q[k])/65536.;ll[k]=log(lik[k]);fixed[k]+=log2(lik[k]/baseprob);}
  double g=global.predict(q);global_saving+=log2((y?g:1-g)/baseprob);global.update(lik,ll,y?g:1-g);
  int pq=quant(pred);prediction_hash^=uint64_t(pq);prediction_hash*=1099511628211ULL;double discrete=(y?pq:65536-pq)/65536.,continuous=y?pred:1-pred;
  double gain=log2(discrete/baseprob);saving+=gain;real_saving+=log2(continuous/baseprob);base-=log2(baseprob);
  size_t block=bits/(8*65536);if(interval.size()<=block)interval.push_back(0);interval[block]+=gain;
  for(int d=0;d<=DEPTH8;d++){auto&n=nodes[route[d]];double l=y?n.plocal:1-n.plocal;n.local_ll+=log(l);
   if(d<DEPTH8){double a=nodes[route[d+1]].pmix;n.split_ll+=log(y?a:1-a);}n.p.update(lik,ll,l);
  }bits++;
 }
};
array<int,K8> candidates8(int p,double a,double b){
 array<int,K8>q;q[0]=p;double l=log(double(p)/(65536-p));
 auto shifted=[&](double d){return d==0?p:quant(1./(1+exp(-(l+d))));};
 q[1]=shifted(-.125);q[2]=shifted(.125);q[3]=shifted(-.1*l);q[4]=shifted(.1*l);
 array<double,4>s={-.125,.25,.5,1};int i=5;for(double x:s)q[i++]=shifted(x*a);for(double x:s)q[i++]=shifted(x*b);
 for(double x:{.25,.5,1.})for(double z:{.25,.5,1.})q[i++]=shifted(x*a+z*b);
 for(double x:{-.5,.5,1.})q[i++]=shifted(.5*(a+b)+x*tanh(a)*tanh(b));
 if(i!=K8)throw runtime_error("candidate enumeration mismatch");return q;
}
struct FastExpert8:Expert{using Expert::Expert;
 void prepare_fast(){for(auto&r:current)r=Row{};
  for(size_t i=0;i<recent.size();i++){int v=recent[i],age=recent.size()-i;if(age<=16)current[3].add(random_word(v,age));}
  if(prev>=0)for(int v:near[prev])current[4].add(v);
  current[7]=getrow(syntax_key(0));current[8]=getrow(syntax_key(1));
  for(int k:{3,4,7,8}){mass[k].clear();for(auto[v,c]:current[k].n)for(int n:path[v])mass[k][n]+=c;}
 }
};
const array<string,4> ARM8={"generic","random_plus_run","grammar_joint","geometry_plus_run"};
string marker8(Expert&x){string marker,text="  <page>\n    <title>";for(size_t i=0;i<text.size();){if(text[i]>='a'&&text[i]<='z'){size_t j=i;while(j<text.size()&&text[j]>='a'&&text[j]<='z')j++;int z=x.ids.at(text.substr(i,j-i));if(z<80)marker+=char(inv(128+z));else if(z<3920){z-=80;marker+=char(inv(208+z/80));marker+=char(inv(128+z%80));}else throw runtime_error("marker dictionary");i=j;}else marker+=char(inv((unsigned char)text[i++]));}return marker;}
void run8(string rp,string pp,string dict,string graph,string constructors,size_t limit,string out){
 auto start=chrono::steady_clock::now();FastExpert8 x(dict,graph,constructors);string raw=readfile(rp),ps=readfile(pp);
 if(ps.size()!=raw.size()*16)throw runtime_error("native trace/input size mismatch");if(limit&&limit<raw.size())raw.resize(limit);
 auto marker=marker8(x);size_t found=raw.find(marker);if(found==string::npos)throw runtime_error("no completed synchronization marker");size_t offset=found+marker.size();x.page_start();
 array<Gate8,4>gates;int node=0;bool escape=false,upper=false,capital=false;vector<int>code;double atomcost=0;
 for(size_t i=offset;i<raw.size();i++){
  if(code.empty()&&!escape)x.prepare_fast();
  for(int j=0;j<8;j++){
   int p=(unsigned char)ps[16*i+2*j]|((unsigned char)ps[16*i+2*j+1]<<8);if(!p)throw runtime_error("invalid zero native probability");int y=((unsigned char)raw[i]>>(7-j))&1;
   auto d=x.deltas(node);double l=log(double(p)/(65536-p));array<pair<double,double>,4>sig={pair<double,double>{1.,clamp(l,-8.,8.)},{d[3],d[8]},{d[7],d[8]},{d[4],d[8]}};
   int state=escape?3:node<0?4:min(2,int(code.size()));int age=x.events<16?0:x.events<256?1:x.events<4096?2:3;
   array<int,DEPTH8>ctx={j,p>>13,state,x.punct,x.prev<0?0:x.cls[x.prev],age};double baseprob=(y?p:65536-p)/65536.;atomcost-=log2(baseprob);
   array<array<int,K8>,4>q;array<double,4>pred;for(int a=0;a<4;a++){q[a]=candidates8(p,sig[a].first,sig[a].second);pred[a]=gates[a].predict(q[a],ctx);}
   // Decoded y is first consumed only here, after all four pre-observation predictions.
   for(int a=0;a<4;a++)gates[a].update(q[a],y,baseprob,pred[a]);
   if(node>=0)node=x.tr[node].c[y];
  }
  int c=inv((unsigned char)raw[i]);if(escape){x.chars(string(1,char(c)),atomcost);escape=false;node=0;atomcost=0;}
  else if(code.empty()&&c==12){escape=true;node=-1;}
  else if(code.empty()&&c<128){if(c==7)upper=true;else if(c==64)capital=true;else if(c==6)upper=false;else{if(!(c>=65&&c<=90)&&!(c>=97&&c<=122))upper=false;if(capital||upper)c=(c-32)&255;capital=false;x.chars(string(1,char(c)),atomcost);}node=0;atomcost=0;}
  else{code.push_back(c);bool done=code.size()==1?c<=207:code.size()==2?c<=207:true;if(done){if(node<0||x.tr[node].leaf<0)throw runtime_error("WRT parse alignment");string s=x.w[x.tr[node].leaf];if(capital){s[0]-=32;capital=false;}if(upper)for(char&a:s)if(a>='a'&&a<='z')a-=32;x.chars(s,atomcost);code.clear();node=0;atomcost=0;}}
  if((i-offset)%65536==0){cerr<<"bytes="<<i-offset;for(int a=0;a<4;a++)cerr<<" "<<ARM8[a]<<"="<<gates[a].saving/8;cerr<<'\n';}
 }
 ofstream f(out);f<<setprecision(17)<<"{\"raw_bytes\":"<<raw.size()<<",\"unscored_prefix_bytes\":"<<offset<<",\"scored_bits\":"<<8*(raw.size()-offset)<<",\"parser_events\":"<<x.events<<",\"literal_words\":"<<x.literals<<",\"pages\":"<<x.pages<<",\"partial_code_bytes_eof\":"<<code.size()<<",\"escape_eof\":"<<(escape?"true":"false")<<",\"arms\":[";
 for(int a=0;a<4;a++){auto&g=gates[a];if(g.bits!=8*(raw.size()-offset)||g.fixed[0]!=0)throw runtime_error("scoring/identity failure");if(a)f<<',';
  f<<"{\"name\":\""<<ARM8[a]<<"\",\"saving_bytes\":"<<g.saving/8<<",\"real_mixture_saving_bytes\":"<<g.real_saving/8<<",\"q16_tax_bytes\":"<<(g.real_saving-g.saving)/8<<",\"global_mixture_saving_bytes\":"<<g.global_saving/8<<",\"baseline_scored_bytes\":"<<g.base/8<<",\"tree_nodes\":"<<g.nodes.size()<<",\"prediction_hash\":\""<<g.prediction_hash<<"\",\"fixed_candidates_saving_bytes\":[";
  for(int k=0;k<K8;k++){if(k)f<<',';f<<g.fixed[k]/8;}f<<"],\"interval_64k_saving_bytes\":[";for(size_t k=0;k<g.interval.size();k++){if(k)f<<',';f<<g.interval[k]/8;}f<<"]}";
 }
 f<<"],\"wall_seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<",\"identity_neutral\":true,\"core_training\":false,\"status\":\"REPLAY_ONLY_NOT_ARCHIVE\",\"deletions\":[]}";
}
void gate_trace8(){int n;if(!(cin>>n))throw runtime_error("trace length");Gate8 g;cout<<setprecision(17);
 for(int t=0;t<n;t++){array<int,K8>q;array<int,DEPTH8>ctx;int y;for(int&v:ctx)cin>>v;for(int&v:q){cin>>v;if(v<1||v>65535)throw runtime_error("trace probability bounds");}cin>>y;double p=g.predict(q,ctx);cout<<p<<'\n';g.update(q,y,(y?q[0]:65536-q[0])/65536.,p);}
}
int main(int argc,char**argv){try{if(argc==2&&string(argv[1])=="gate_trace"){gate_trace8();return 0;}if(argc!=8){cerr<<"raw final_p dictionary graph constructors limit out\n";return 2;}run8(argv[1],argv[2],argv[3],argv[4],argv[5],stoull(argv[6]),argv[7]);return 0;}catch(exception&e){cerr<<e.what()<<'\n';return 1;}}
