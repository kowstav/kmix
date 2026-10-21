#include "research_round8_clean_title_library.h"
struct WrtState8{int node=0;bool escape=false,upper=false,capital=false;vector<int>code;double cost=0;};
void finish_byte8(CleanExpert8&x,WrtState8&s,unsigned char raw,double cost){
 s.cost+=cost;for(int j=7;j>=0;j--)if(s.node>=0)s.node=x.tr[s.node].c[(raw>>j)&1];int c=inv(raw);
 if(s.escape){x.chars(string(1,char(c)),s.cost);s.escape=false;s.node=0;s.cost=0;}
 else if(s.code.empty()&&c==12){s.escape=true;s.node=-1;}
 else if(s.code.empty()&&c<128){if(c==7)s.upper=true;else if(c==64)s.capital=true;else if(c==6)s.upper=false;else{if(!(c>=65&&c<=90)&&!(c>=97&&c<=122))s.upper=false;if(s.capital||s.upper)c=(c-32)&255;s.capital=false;x.chars(string(1,char(c)),s.cost);}s.node=0;s.cost=0;}
 else{s.code.push_back(c);bool done=s.code.size()==1?c<=207:s.code.size()==2?c<=207:true;if(done){if(s.node<0||x.tr[s.node].leaf<0)throw runtime_error("warm WRT alignment");string word=x.w[x.tr[s.node].leaf];if(s.capital){word[0]-=32;s.capital=false;}if(s.upper)for(char&a:word)if(a>='a'&&a<='z')a-=32;x.chars(word,s.cost);s.code.clear();s.node=0;s.cost=0;}}
}
struct Query8{string name,raw,p;size_t start;};
void warm8(string fullpath,string dict,string graph,string cons,string P,string out){
 auto begun=chrono::steady_clock::now();CleanExpert8 x(dict,graph,cons);string full=readfile(fullpath);auto mark=marker8(x);auto first=full.find(mark);if(first==string::npos)throw runtime_error("full synchronization absent");size_t cursor=first+mark.size();x.initial_sync();WrtState8 state;
 vector<Query8>qs={{"a",P+"/preserved/slices/a2m.bin",P+"/lex_finalbit_2m_v1/a/final_p.u16",0},{"c",P+"/c2m.bin",P+"/lex_finalbit_2m_v1/c/final_p.u16",100000000},{"b",P+"/preserved/slices/b2m.bin",P+"/lex_finalbit_2m_v1/b/final_p.u16",102635191},{"d",P+"/d2m.bin",P+"/lex_finalbit_2m_v1/d/final_p.u16",180000000}};
 ofstream f(out);f<<setprecision(17)<<"{\"status\":\"WARM_SOURCE_COLD_CORE_CONDITIONAL_DIAGNOSTIC\",\"future_source_bytes_used\":false,\"core_retraining\":false,\"queries\":[";bool comma=false;
 for(auto&qy:qs){string raw=readfile(qy.raw),ps=readfile(qy.p);if(ps.size()!=raw.size()*16||qy.start+raw.size()>full.size()||full.compare(qy.start,raw.size(),raw)!=0)throw runtime_error("full/slice exact equality");raw.resize(131072);auto local=raw.find(mark);if(local==string::npos)throw runtime_error("query synchronization absent");size_t offset=local+mark.size(),stop=qy.start+offset;if(stop<cursor)throw runtime_error("nonmonotonic queries");auto ws=chrono::steady_clock::now();
  while(cursor<stop)finish_byte8(x,state,(unsigned char)full[cursor++],0);
  if(state.node!=0||!state.code.empty()||state.escape||x.role()!=1||x.tag||x.entity)throw runtime_error("warm observer not aligned at completed title marker");
  double warmsec=chrono::duration<double>(chrono::steady_clock::now()-ws).count();size_t seen=0;for(double v:x.counts)seen+=v>0;auto before=x.events;array<Gate8,6>gates;
  for(size_t i=offset;i<raw.size();i++){
   if(state.code.empty()&&!state.escape)x.prepare_clean();double bytecost=0;int predictive_node=state.node;
   for(int j=0;j<8;j++){
    int p=(unsigned char)ps[16*i+2*j]|((unsigned char)ps[16*i+2*j+1]<<8);if(!p)throw runtime_error("zero native probability");int y=((unsigned char)raw[i]>>(7-j))&1;auto d=x.deltas(predictive_node);double l=log(double(p)/(65536-p));bool prose=x.lex_text&&!x.tag&&!x.entity;
    array<pair<double,double>,6>sig={pair<double,double>{1.,clamp(l,-8.,8.)},{prose?d[0]:0,prose?d[8]:0},{prose?d[1]:0,prose?d[8]:0},{prose?d[4]:0,prose?d[8]:0},{prose?d[10]:0,prose?d[8]:0},{prose?d[11]:0,prose?d[8]:0}};
    auto age=x.events-x.page_event0;array<int,DEPTH8>ctx={j,p>>13,state.escape?3:predictive_node<0?4:min(2,int(state.code.size())),x.punct,x.role(),age<16?0:age<128?1:age<1024?2:3};double base=(y?p:65536-p)/65536.;bytecost-=log2(base);
    array<array<int,K8>,6>cp;array<double,6>pr;for(int a=0;a<6;a++){cp[a]=candidates8(p,sig[a].first,sig[a].second);pr[a]=gates[a].predict(cp[a],ctx);}for(int a=0;a<6;a++)gates[a].update(cp[a],y,base,pr[a]);if(predictive_node>=0)predictive_node=x.tr[predictive_node].c[y];
   }
   finish_byte8(x,state,(unsigned char)raw[i],bytecost);if(state.node!=0&&state.node!=predictive_node)throw runtime_error("split bit/byte traversal mismatch");cursor++;
  }
  if(comma)f<<',';comma=true;f<<"{\"slice\":\""<<qy.name<<"_warm128k\",\"start\":"<<qy.start<<",\"raw_bytes\":"<<raw.size()<<",\"unscored_prefix_bytes\":"<<offset<<",\"prefix_dictionary_words_seen\":"<<seen<<",\"dictionary_words\":"<<x.w.size()<<",\"prefix_events_before_scoring\":"<<before<<",\"warm_processing_seconds\":"<<warmsec<<",\"source_cursor_after_scoring\":"<<cursor<<",\"past_bank_after\":"<<x.bank.size()<<",\"arms\":[";
  for(int a=0;a<6;a++){auto&g=gates[a];if(g.bits!=8*(raw.size()-offset)||g.fixed[0]!=0)throw runtime_error("score/identity");if(a)f<<',';f<<"{\"name\":\""<<CLEAN_ARM8[a]<<"\",\"saving_bytes\":"<<g.saving/8<<",\"q16_tax_bytes\":"<<(g.real_saving-g.saving)/8<<",\"prediction_hash\":\""<<g.prediction_hash<<"\"}";}f<<"]}";f.flush();cerr<<"completed="<<qy.name<<" prefix_seen="<<seen<<" past_events="<<before<<"\n";
 }
 f<<"],\"wall_seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-begun).count()<<",\"core_state\":\"COLD_EXISTING_TRACE\",\"source_state\":\"GENUINE_DECODED_PREFIX_ONLY\",\"archive_claim\":false,\"deletions\":[]}";
}
int main(int argc,char**argv){try{if(argc!=7)return 2;warm8(argv[1],argv[2],argv[3],argv[4],argv[5],argv[6]);return 0;}catch(exception&e){cerr<<e.what()<<'\n';return 1;}}
