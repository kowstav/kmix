#include "research_round8_conditional_library.h"
struct CleanExpert8:FastExpert8{
 using FastExpert8::FastExpert8;
 bool tag=false,lex_title=false,lex_text=false,entity=false;char quote=0;string tagbuf,entitybuf;uint64_t page_event0=0;
 uint64_t ce=~0ULL,cs=~0ULL,cp=~0ULL;int cr=-1,cu=-1;
 int role()const{return lex_title?1:lex_text?2:0;}
 void lexical(char c,double cost){if(!lex_title&&!lex_text)return;char lower=(c>='A'&&c<='Z')?c+32:c;
  if(lower>='a'&&lower<='z'){if(ascii.size()<128)ascii+=lower;else ascii.back()='#';ascii_cost+=cost;}
  else{commit();if(c=='.'||c=='!'||c=='?')punct=1;else if(c==','||c==';'||c==':')punct=2;else if(c=='\n'||c=='<'||c=='>')punct=3;}
 }
 void close_tag(){string s=tagbuf;bool closing=!s.empty()&&s[0]=='/';size_t i=closing?1:0,j=i;while(j<s.size()&&((s[j]>='a'&&s[j]<='z')||(s[j]>='A'&&s[j]<='Z')))j++;string name=s.substr(i,j-i);for(char&a:name)if(a>='A'&&a<='Z')a+=32;
  if(name=="page"){if(closing){page_end();lex_title=lex_text=false;title=false;}else{page_start();page_event0=events;lex_title=lex_text=false;title=false;}}
  else if(name=="title"){lex_title=!closing;title=lex_title;}
  else if(name=="text")lex_text=!closing;
  punct=3;tag=false;tagbuf.clear();quote=0;
 }
 void entity_done(double cost){char c=' ';if(entitybuf=="amp")c='&';else if(entitybuf=="lt")c='<';else if(entitybuf=="gt")c='>';else if(entitybuf=="quot")c='"';else if(entitybuf=="apos")c='\'';
  else if(!entitybuf.empty()&&entitybuf[0]=='#'){try{size_t pos=0;unsigned long a=stoul(entitybuf.substr(entitybuf.size()>1&&(entitybuf[1]=='x'||entitybuf[1]=='X')?2:1),&pos,entitybuf.size()>1&&(entitybuf[1]=='x'||entitybuf[1]=='X')?16:10);if(a<128)c=char(a);}catch(...){} }
  lexical(c,cost);entity=false;entitybuf.clear();
 }
 void chars(const string&s,double cost){for(char c:s){double part=cost/max(size_t(1),s.size());
  if(tag){tagbuf+=c;if(tagbuf.size()>4096)throw runtime_error("XML observer tag bound exceeded");
   bool comment=tagbuf.rfind("!--",0)==0;if(comment){if(tagbuf.size()>=3&&tagbuf.substr(tagbuf.size()-3)=="-->")close_tag();continue;}
   if(quote){if(c==quote)quote=0;}else if(c=='\''||c=='"')quote=c;else if(c=='>')close_tag();continue;
  }
  if(entity){if(c==';')entity_done(part);else{entitybuf+=c;if(entitybuf.size()>32){lexical(' ',part);entity=false;entitybuf.clear();}}continue;}
  if(c=='<'){commit();tag=true;tagbuf.clear();quote=0;continue;}
  if(c=='&'&&(lex_title||lex_text)){entity=true;entitybuf.clear();continue;}
  lexical(c,part);
 }}
 void initial_sync(){page_start();lex_title=true;lex_text=false;title=true;page_event0=events;}
 void prepare_clean(){if(ce==events&&cs==serial&&cp==pages&&cr==role()&&cu==punct)return;ce=events;cs=serial;cp=pages;cr=role();cu=punct;
  for(auto&r:current)r=Row{};
  for(int v:title_keys){current[0].add(v);current[1].add(random_word(v,0));for(int n:near[v])current[4].add(n);}
  current[8]=getrow(syntax_key(1));vector<pair<int,int>>rank;
  for(size_t j=0;j<bank.size();j++){int overlap=0;for(int v:title_keys)overlap+=bank[j].keys.count(v);if(overlap)rank.push_back({-overlap,int(j)});}sort(rank.begin(),rank.end());
  for(size_t i=0;i<min(size_t(4),rank.size());i++){int j=rank[i].second;for(auto[v,n]:bank[j].words.n)current[10].add(v,n);int r=(uint32_t(j)*2654435761u+uint32_t(events))%bank.size();for(auto[v,n]:bank[r].words.n)current[11].add(v,n);donors++;}
  for(int k:{0,1,4,8,10,11}){mass[k].clear();for(auto[v,n]:current[k].n)for(int t:path[v])mass[k][t]+=n;}
 }
};
const array<string,6> CLEAN_ARM8={"generic","persistent_title","random_title","title_geometry","past_title_retrieval","random_past_retrieval"};
void clean_selftest8(string dict,string graph,string cons){
 Expert old(dict,graph,cons);old.page_start();old.chars("<title>aardvark</title> ",10);if(!old.title_keys.count(old.ids.at("title")))throw runtime_error("old contamination not reproduced");
 CleanExpert8 x(dict,graph,cons);x.chars("<page><title>aardvark</title><timestamp>title</timestamp><text a=\"x>y\">the aardvark &amp; the &#97;ardvark </text></page>",20);
 if(x.counts[x.ids.at("title")]!=0||x.bank.size()!=1||x.bank[0].keys.count(x.ids.at("title"))||!x.bank[0].keys.count(x.ids.at("aardvark")))throw runtime_error("semantic XML/title bank check");
 if(x.counts[x.ids.at("aardvark")]!=4)throw runtime_error("entity decoding count");
 x.chars("<page><title>aardvark</title><text>the ",10);x.prepare_clean();if(x.current[0].total<1||x.current[10].total<1)throw runtime_error("prefix-only title/past retrieval");
 double worst=0;for(int k:{0,1,4,8,10,11}){double z=0;for(size_t v=0;v<x.w.size();v++)z+=x.e(k,x.path[v].back());worst=max(worst,abs(z-1));if(abs(z-1)>1e-10)throw runtime_error("mass normalization");}
 auto events=x.events;x.chars("uncompleted&#",3);x.prepare_clean();if(x.events!=events||!x.entity)throw runtime_error("EOF prematurely completed");
 cout<<"{\"status\":\"PASS\",\"old_title_tag_contamination_reproduced\":true,\"tag_and_metadata_words_excluded\":true,\"quote_aware_tag_close\":true,\"entities_delayed_until_complete\":true,\"completed_past_bank_only\":true,\"incomplete_EOF_unflushed\":true,\"max_mass_normalization_error\":"<<setprecision(17)<<worst<<"}"<<'\n';
}
void run_clean8(string rp,string pp,string dict,string graph,string cons,size_t limit,string out){
 auto start=chrono::steady_clock::now();CleanExpert8 x(dict,graph,cons);string raw=readfile(rp),ps=readfile(pp);if(ps.size()!=raw.size()*16)throw runtime_error("trace/input size");if(limit&&limit<raw.size())raw.resize(limit);auto mark=marker8(x);auto found=raw.find(mark);if(found==string::npos)throw runtime_error("sync absent");size_t offset=found+mark.size();x.initial_sync();array<Gate8,6>gates;int node=0;bool escape=false,upper=false,capital=false;vector<int>code;double atomcost=0;
 for(size_t i=offset;i<raw.size();i++){
  if(code.empty()&&!escape)x.prepare_clean();
  for(int j=0;j<8;j++){
   int p=(unsigned char)ps[16*i+2*j]|((unsigned char)ps[16*i+2*j+1]<<8);if(!p)throw runtime_error("p=0");int y=((unsigned char)raw[i]>>(7-j))&1;auto d=x.deltas(node);double l=log(double(p)/(65536-p));bool prose=x.lex_text&&!x.tag&&!x.entity;
   array<pair<double,double>,6>sig={pair<double,double>{1.,clamp(l,-8.,8.)},{prose?d[0]:0,prose?d[8]:0},{prose?d[1]:0,prose?d[8]:0},{prose?d[4]:0,prose?d[8]:0},{prose?d[10]:0,prose?d[8]:0},{prose?d[11]:0,prose?d[8]:0}};
   auto age=x.events-x.page_event0;array<int,DEPTH8>ctx={j,p>>13,escape?3:node<0?4:min(2,int(code.size())),x.punct,x.role(),age<16?0:age<128?1:age<1024?2:3};double base=(y?p:65536-p)/65536.;atomcost-=log2(base);
   array<array<int,K8>,6>q;array<double,6>pred;for(int a=0;a<6;a++){q[a]=candidates8(p,sig[a].first,sig[a].second);pred[a]=gates[a].predict(q[a],ctx);}for(int a=0;a<6;a++)gates[a].update(q[a],y,base,pred[a]);if(node>=0)node=x.tr[node].c[y];
  }
  int c=inv((unsigned char)raw[i]);if(escape){x.chars(string(1,char(c)),atomcost);escape=false;node=0;atomcost=0;}
  else if(code.empty()&&c==12){escape=true;node=-1;}
  else if(code.empty()&&c<128){if(c==7)upper=true;else if(c==64)capital=true;else if(c==6)upper=false;else{if(!(c>=65&&c<=90)&&!(c>=97&&c<=122))upper=false;if(capital||upper)c=(c-32)&255;capital=false;x.chars(string(1,char(c)),atomcost);}node=0;atomcost=0;}
  else{code.push_back(c);bool done=code.size()==1?c<=207:code.size()==2?c<=207:true;if(done){if(node<0||x.tr[node].leaf<0)throw runtime_error("WRT parser");string s=x.w[x.tr[node].leaf];if(capital){s[0]-=32;capital=false;}if(upper)for(char&a:s)if(a>='a'&&a<='z')a-=32;x.chars(s,atomcost);code.clear();node=0;atomcost=0;}}
 }
 ofstream f(out);f<<setprecision(17)<<"{\"raw_bytes\":"<<raw.size()<<",\"unscored_prefix_bytes\":"<<offset<<",\"scored_bits\":"<<8*(raw.size()-offset)<<",\"lexical_events\":"<<x.events<<",\"past_bank\":"<<x.bank.size()<<",\"donor_selections\":"<<x.donors<<",\"entity_EOF\":"<<(x.entity?"true":"false")<<",\"arms\":[";
 for(int a=0;a<6;a++){auto&g=gates[a];if(g.bits!=8*(raw.size()-offset)||g.fixed[0]!=0)throw runtime_error("identity/accounting");if(a)f<<',';f<<"{\"name\":\""<<CLEAN_ARM8[a]<<"\",\"saving_bytes\":"<<g.saving/8<<",\"q16_tax_bytes\":"<<(g.real_saving-g.saving)/8<<",\"tree_nodes\":"<<g.nodes.size()<<",\"prediction_hash\":\""<<g.prediction_hash<<"\"}";}
 f<<"],\"wall_seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<",\"status\":\"CLEAN_TITLE_REPLAY_NOT_ARCHIVE\",\"core_training\":false,\"deletions\":[]}";
}
int main(int argc,char**argv){try{if(argc==5&&string(argv[1])=="selftest"){clean_selftest8(argv[2],argv[3],argv[4]);return 0;}if(argc!=8)return 2;run_clean8(argv[1],argv[2],argv[3],argv[4],argv[5],stoull(argv[6]),argv[7]);return 0;}catch(exception&e){cerr<<e.what()<<'\n';return 1;}}
