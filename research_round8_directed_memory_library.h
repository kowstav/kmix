#include "research_round8_clean_library.h"
struct CleanExpert8:FastExpert8{
 using FastExpert8::FastExpert8;
 bool tag=false,lex_title=false,lex_text=false,entity=false;char quote=0;string tagbuf,tagtail,entitybuf;uint64_t page_event0=0,tag_truncations=0;
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
  punct=3;tag=false;tagbuf.clear();tagtail.clear();quote=0;
 }
 void entity_done(double cost){char c=' ';if(entitybuf=="amp")c='&';else if(entitybuf=="lt")c='<';else if(entitybuf=="gt")c='>';else if(entitybuf=="quot")c='"';else if(entitybuf=="apos")c='\'';
  else if(!entitybuf.empty()&&entitybuf[0]=='#'){try{size_t pos=0;unsigned long a=stoul(entitybuf.substr(entitybuf.size()>1&&(entitybuf[1]=='x'||entitybuf[1]=='X')?2:1),&pos,entitybuf.size()>1&&(entitybuf[1]=='x'||entitybuf[1]=='X')?16:10);if(a<128)c=char(a);}catch(...){} }
  lexical(c,cost);entity=false;entitybuf.clear();
 }
 void chars(const string&s,double cost){for(char c:s){double part=cost/max(size_t(1),s.size());
  if(tag){if(tagbuf.size()<128)tagbuf+=c;else if(tagbuf.size()==128){tagbuf+=char(0);tag_truncations++;}tagtail+=c;if(tagtail.size()>3)tagtail.erase(tagtail.begin());
   bool comment=tagbuf.rfind("!--",0)==0;if(comment){if(tagtail=="-->")close_tag();continue;}
   if(quote){if(c==quote)quote=0;}else if(c=='\''||c=='"')quote=c;else if(c=='>')close_tag();continue;
  }
  if(entity){if(c==';')entity_done(part);else{entitybuf+=c;if(entitybuf.size()>32){lexical(' ',part);entity=false;entitybuf.clear();}}continue;}
  if(c=='<'){commit();tag=true;tagbuf.clear();tagtail.clear();quote=0;continue;}
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

struct DirectedRow8{int source=-1;array<int,8>target{};array<uint16_t,8>count{};
 void add(int key,int v,unsigned amount){if(source!=key){source=key;count.fill(0);}int chosen=-1;for(int i=0;i<8;i++)if(count[i]&&target[i]==v)chosen=i;if(chosen<0)for(int i=0;i<8;i++)if(!count[i]){chosen=i;target[i]=v;break;}if(chosen<0){chosen=0;for(int i=1;i<8;i++)if(count[i]<count[chosen]||(count[i]==count[chosen]&&target[i]<target[chosen]))chosen=i;target[chosen]=v;}if(unsigned(count[chosen])+amount>65535)for(auto&c:count)c=(unsigned(c)+1)/2;count[chosen]+=amount;}
};
struct DirectedExpert8:CleanExpert8{
 array<DirectedRow8,1024>next,wide;vector<int>pending;uint64_t de=~0ULL,ds=~0ULL,dp=~0ULL;int dr=-1,du=-1;
 using CleanExpert8::CleanExpert8;
 int random_word(int v,int salt)const{int lo=(v/256)*256,hi=min(int(w.size()),lo+256);vector<int>pool;for(int j=lo;j<hi;j++)if(w[j].size()==w[v].size()&&cls[j]==cls[v])pool.push_back(j);if(pool.empty())return v;return pool[(uint32_t(v)*2654435761u+uint32_t(salt)*2246822519u)%pool.size()];}
 static size_t slot(int v){return (uint32_t(v)*2654435761u)&1023;}
 void learned(int v){if(cls[v]!=2)return;if(!pending.empty())next[slot(pending.back())].add(pending.back(),v,1);int age=0;for(int i=int(pending.size())-1;i>=0&&age<8;i--,age++)wide[slot(pending[i])].add(pending[i],v,8-age);pending.push_back(v);if(pending.size()>8)pending.erase(pending.begin());}
 void chars(const string&s,double cost){for(char c:s){uint64_t previous=events,pp=pages;CleanExpert8::chars(string(1,c),cost/max(size_t(1),s.size()));if(pages!=pp)pending.clear();if(events!=previous){if(events!=previous+1||recent.empty())throw runtime_error("directed commit accounting");learned(recent.back());}}}
 void prepare_clean(){if(de==events&&ds==serial&&dp==pages&&dr==role()&&du==punct)return;de=events;ds=serial;dp=pages;dr=role();du=punct;for(auto&r:current)r=Row{};
  auto add=[&](int a,int b,const DirectedRow8&r){if(r.source!=lastcontent)return;for(int i=0;i<8;i++)if(r.count[i]){current[a].add(r.target[i],r.count[i]);current[b].add(random_word(r.target[i],i),r.count[i]);}};
  if(lastcontent>=0){add(0,1,next[slot(lastcontent)]);add(10,11,wide[slot(lastcontent)]);}int age=0;for(int i=int(recent.size())-1;i>=0&&age<16;i--)if(cls[recent[i]]==2){current[4].add(recent[i]);age++;}current[8]=getrow(syntax_key(1));
  for(int k:{0,1,4,8,10,11}){mass[k].clear();for(auto[v,n]:current[k].n)for(int t:path[v])mass[k][t]+=n;}
 }
};
void directed_selftest8(string dict,string graph,string cons){
 DirectedExpert8 x(dict,graph,cons);x.chars("<page><title>aardvark</title><text>aardvark zebra aardvark zebra aardvark ",1);x.prepare_clean();int a=x.ids.at("aardvark"),z=x.ids.at("zebra");auto&r=x.next[x.slot(a)];bool found=false;for(int i=0;i<8;i++)found|=r.count[i]&&r.target[i]==z;if(r.source!=a||!found)throw runtime_error("directed pair not learned");auto old=x.current[0].n;x.chars("uncompleted",1);x.prepare_clean();if(old!=x.current[0].n)throw runtime_error("unfinished word entered memory");double worst=0;for(int k:{0,1,4,8,10,11}){double sum=0;for(size_t v=0;v<x.w.size();v++)sum+=x.e(k,x.path[v].back());worst=max(worst,abs(sum-1));}if(worst>1e-10)throw runtime_error("directed normalization");
 x.chars("</text></page><page><title>",1);if(!x.pending.empty())throw runtime_error("article pending sources not reset");DirectedRow8 q;for(int i=0;i<200000;i++)q.add(1,i%17,8);for(auto c:q.count)if(c>65535)throw runtime_error("counter overflow");q.add(2,3,1);if(q.source!=2||q.count[0]!=1)throw runtime_error("row collision replacement");
 cout<<"{\"status\":\"PASS\",\"pair_learning\":true,\"unfinished_word_noninterference\":true,\"article_pending_reset\":true,\"normalization_error\":"<<setprecision(17)<<worst<<",\"counter_and_collision_checks\":true,\"packed_two_model_row_bytes_design\":69632,\"instrumented_two_row_arrays_bytes\":"<<2*sizeof(x.next)<<"}"<<'\n';
}
