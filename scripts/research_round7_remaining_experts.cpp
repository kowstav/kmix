// Bounded causal experts. Every prediction sees only the decoded prefix.
// Replay observer: does not change the original cmix predictor trajectory.
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;
constexpr int F=15;
const array<string,F> fn={"echo16","echo128","empty","rank_length_random","integer_geometry","anagram","phonetic","syntax","constructor_run","source_surprise","article_retrieval","article_random","hazard16","hazard128","newmention"};
const array<double,4> strengths={-.125,.125,.5,1.};
int inv(int c){if(c>=123&&c<127)c+=80-123;else if(c>=80&&c<84)c-=80-123;else if((c>=58&&c<=63)||(c>=74&&c<=79))c^=0x70;if(c==88||c==96)c^=88^96;return c;}
string readfile(string p){ifstream f(p,ios::binary);if(!f)throw runtime_error("missing input "+p);return string(istreambuf_iterator<char>(f),{});}
struct Node{int c[2]={-1,-1},leaf=-1;double rank=0,count=0,seen=0;};
struct Row{map<int,double> n;double total=0;uint64_t age=0;void add(int w,double v=1){n[w]+=v;total+=v;if(n.size()>32){auto it=min_element(n.begin(),n.end(),[](auto&a,auto&b){return a.second<b.second||(a.second==b.second&&a.first<b.first);});total-=it->second;n.erase(it);}}};
struct Article{Row words;set<int> keys;uint64_t serial=0;};
struct Expert {
 vector<string>w;vector<vector<int>>path,near;vector<int>cls;vector<Node>tr;unordered_map<string,int> ids;
 unordered_map<uint64_t,Row>rows;vector<int> recent;vector<int64_t>last;vector<double>counts;
 map<int,int>article_counts;set<int>title_keys;vector<Article>bank;Row article;
 array<Row,F> current;array<unordered_map<int,double>,F>mass;
 uint64_t events=0,serial=0;double total=0;int prev=-1,lastcontent=-1,run=0,punct=0,surprise=0;
 string ascii,tail;bool title=false;double wordcost=0,ascii_cost=0;uint64_t literals=0,pages=0,donors=0;
 Expert(string dictionary,string graph,string constructors){
  string d=readfile(dictionary);regex rx("[a-z]+");for(sregex_iterator it(d.begin(),d.end(),rx),end;it!=end;++it)w.push_back(it->str());
  string cs=readfile(constructors);set<string>fun;istringstream cf(cs);string s;while(cf>>s)fun.insert(s);
  tr.emplace_back();path.resize(w.size());near.resize(w.size());cls.resize(w.size());counts.assign(w.size(),0);last.assign(w.size(),-1);
  ifstream gf(graph);for(size_t j=0;j<w.size();j++){for(int k=0,x;k<8;k++){gf>>x;if(!gf||x<0||x>=int(w.size()))throw runtime_error("graph alignment");near[j].push_back(x);}}
  map<string,vector<int>>an,ph;
  for(size_t j=0;j<w.size();j++){ids[w[j]]=j;cls[j]=fun.count(w[j])?1:2;string a=w[j];sort(a.begin(),a.end());an[a].push_back(j);ph[soundex(w[j])].push_back(j);
   vector<int>c;if(j<80)c={128+int(j)};else if(j<3920){int k=j-80;c={208+k/80,128+k%80};}else{int k=j-3920;c={240+(k/80)/32,208+(k/80)%32,128+k%80};}
   int node=0;path[j].push_back(0);for(int x:c){int b=inv(x);for(int k=7;k>=0;k--){int y=(b>>k)&1;if(tr[node].c[y]<0){tr[node].c[y]=tr.size();tr.emplace_back();}node=tr[node].c[y];path[j].push_back(node);}}assert(tr[node].leaf<0&&tr[node].c[0]<0&&tr[node].c[1]<0);tr[node].leaf=j;
  }
  double z=0;for(size_t j=0;j<w.size();j++)z+=1./(j+1.);for(size_t j=0;j<w.size();j++)for(int n:path[j])tr[n].rank+=1./(j+1.)/z;
  anagrams=move(an);phonetics=move(ph);
 }
 map<string,vector<int>>anagrams,phonetics;
 static string soundex(string s){string out(1,s[0]);string code="01230120022455012623010202";char old=code[s[0]-'a'];for(size_t i=1;i<s.size()&&out.size()<4;i++){char c=code[s[i]-'a'];if(c!='0'&&c!=old)out+=c;old=c;}while(out.size()<4)out+='0';return out;}
 uint64_t syntax_key(int kind)const {uint64_t k=kind+1; k=k*4+(prev<0?0:cls[prev]);k=k*4+punct;if(kind==1){k=k*5+min(run,4);k=k*8+(lastcontent<0?0:min(lastcontent/6000,7));}if(kind==2){k=k*4+surprise;k=k*8+(prev<0?0:min(prev/6000,7));}return k;}
 Row getrow(uint64_t key){auto it=rows.find(key);return it==rows.end()?Row{}:it->second;}
 void learn(uint64_t key,int v){if(rows.size()>=4096&&!rows.count(key)){auto it=min_element(rows.begin(),rows.end(),[](auto&a,auto&b){return a.second.age<b.second.age||(a.second.age==b.second.age&&a.first<b.first);});rows.erase(it);}auto&r=rows[key];r.add(v);r.age=events;}
 void commit(){if(ascii.empty())return;auto it=ids.find(ascii);if(it==ids.end()){literals++;prev=-1;run=0;}else{
   int v=it->second;for(int k=0;k<3;k++)learn(syntax_key(k),v);
   bool seen=article_counts.count(v);for(int n:path[v]){tr[n].count++;tr[n].seen+=seen?1:(counts[v]+1+64./(v+1.)/rank_z());}
   counts[v]++;total++;last[v]=events;article_counts[v]++;article.add(v);if(title&&cls[v]==2)title_keys.insert(v);
   recent.push_back(v);if(recent.size()>128)recent.erase(recent.begin());prev=v;if(cls[v]==1)run++;else{run=0;lastcontent=v;}surprise=min(3,int(ascii_cost/max(1,int(ascii.size()))/2));events++;
  }ascii.clear();ascii_cost=0;
 }
 double rank_z()const {static double z=0;if(z==0)for(size_t j=0;j<w.size();j++)z+=1./(j+1.);return z;}
 void page_start(){commit();article=Row{};article_counts.clear();title_keys.clear();for(auto&n:tr)n.seen=0;recent.clear();prev=lastcontent=-1;run=punct=surprise=0;title=true;pages++;}
 void page_end(){commit();if(!title_keys.empty()&&article.total>0){if(bank.size()==1024)bank.erase(bank.begin());bank.push_back({article,title_keys,serial++});}title=false;}
 void chars(const string&s,double cost){for(unsigned char c:s){char lower=(c>='A'&&c<='Z')?c+32:c;bool letter=lower>='a'&&lower<='z';if(letter){if(ascii.size()<128)ascii+=lower;else ascii.back()='#';ascii_cost+=cost/max(size_t(1),s.size());}else{commit();if(c=='.'||c=='!'||c=='?')punct=1;else if(c==','||c==';'||c==':')punct=2;else if(c=='\n'||c=='<'||c=='>')punct=3;}
   tail+=lower;if(tail.size()>32)tail.erase(tail.begin());if(ends("<page>"))page_start();if(ends("<title>"))title=true;if(ends("</title>")){commit();title=false;}if(ends("</page>"))page_end();
  }}
 bool ends(string s){return tail.size()>=s.size()&&tail.compare(tail.size()-s.size(),s.size(),s)==0;}
 int random_word(int v,int slot)const{int lo=max(0,(v/256)*256),hi=min(int(w.size()),lo+256);vector<int>pool;for(int j=lo;j<hi;j++)if(w[j].size()==w[v].size())pool.push_back(j);if(pool.empty())return v;return pool[(uint32_t(v)*2654435761u+slot*2246822519u)%pool.size()];}
 void prepare(){for(auto&r:current)r=Row{};
  for(size_t i=0;i<recent.size();i++){int v=recent[i],age=recent.size()-i;current[1].add(v);if(age<=16)current[0].add(v);if(age<=16)current[3].add(random_word(v,age));current[12].add(v,exp2(-age/16.));current[13].add(v,exp2(-age/128.));}
  if(prev>=0){for(int v:near[prev])current[4].add(v);string a=w[prev];sort(a.begin(),a.end());auto addlist=[&](int k,const vector<int>&vs){for(size_t i=0;i<min(size_t(32),vs.size());i++)if(vs[i]!=prev)current[k].add(vs[i]);};addlist(5,anagrams[a]);addlist(6,phonetics[soundex(w[prev])]);}
  current[7]=getrow(syntax_key(0));current[8]=getrow(syntax_key(1));current[9]=getrow(syntax_key(2));
  vector<pair<int,int>>rank;for(size_t j=0;j<bank.size();j++){int overlap=0;for(int k:title_keys)overlap+=bank[j].keys.count(k);if(overlap)rank.push_back({-overlap,int(j)});}sort(rank.begin(),rank.end());for(size_t q=0;q<min(size_t(4),rank.size());q++){donors++;int j=rank[q].second;for(auto [v,n]:bank[j].words.n)current[10].add(v,n);int randomj=(uint32_t(j)*2654435761u+uint32_t(events))%bank.size();for(auto [v,n]:bank[randomj].words.n)current[11].add(v,n);}
  for(int k=0;k<F;k++){mass[k].clear();for(auto[v,c]:current[k].n)for(int n:path[v])mass[k][n]+=c;}
 }
 double g(int node)const{return node<0?0:(tr[node].count+64*tr[node].rank)/(total+64);}
 double e(int k,int node){if(node<0)return 0;double prior=g(node);if(k==14){double den=total+64-tr[0].seen;return den>1e-12?max(0.,tr[node].count+64*tr[node].rank-tr[node].seen)/den:prior;}auto it=mass[k].find(node);double m=it==mass[k].end()?0:it->second;return (m+16*prior)/(current[k].total+16);}
 array<double,F> deltas(int node){array<double,F>d{};if(node<0)return d;int a=tr[node].c[0],b=tr[node].c[1];if(a<0||b<0)return d;double ga=g(a),gb=g(b),base=log(gb/ga);for(int k=0;k<F;k++){double ea=e(k,a),eb=e(k,b);d[k]=clamp(log(max(eb,1e-15)/max(ea,1e-15))-base,-8.,8.);}return d;}
};
struct Stats{vector<double>gain;double mixgain=0,baseline=0;uint64_t bits=0;map<int,vector<double>>post;};
int quant(double p){return clamp(int(floor(p*65536+.5)),1,65535);}
void run(string rawpath,string ppath,string dictionary,string graph,string constructors,size_t limit,string outpath){
 auto begun=chrono::steady_clock::now();Expert x(dictionary,graph,constructors);string raw=readfile(rawpath), ps=readfile(ppath);assert(ps.size()==raw.size()*16);if(limit&&raw.size()>limit)raw.resize(limit);
 // Start only after a fully observed page/title synchronization marker.
 string marker;string text="  <page>\n    <title>";regex words("[a-z]+");for(size_t i=0;i<text.size();){if(text[i]>='a'&&text[i]<='z'){size_t j=i;while(j<text.size()&&text[j]>='a'&&text[j]<='z')j++;int v=x.ids.at(text.substr(i,j-i));int z=v;if(z<80)marker+=char(inv(128+z));else if(z<3920){z-=80;marker+=char(inv(208+z/80));marker+=char(inv(128+z%80));}else throw runtime_error("marker dictionary");i=j;}else marker+=char(inv((unsigned char)text[i++]));}
 size_t found=raw.find(marker);if(found==string::npos)throw runtime_error("synchronization absent");size_t offset=found+marker.size();x.page_start();
 constexpr int M=1+F*4;Stats st;st.gain.assign(M,0);int node=0;bool escape=false,upper=false,capital=false;vector<int>code;double atomcost=0;vector<int>q(M);vector<double>ll(M);vector<double>pri(M,-log(2.*(M-1)));pri[0]=-log(2.);
 for(size_t i=offset;i<raw.size();i++){
  if(code.empty()&&!escape)x.prepare();
  for(int j=0;j<8;j++){
   uint16_t p=(unsigned char)ps[16*i+2*j]|(uint16_t((unsigned char)ps[16*i+2*j+1])<<8);assert(p);int y=((unsigned char)raw[i]>>(7-j))&1;auto d=x.deltas(node);double logit=log(double(p)/(65536-p));q[0]=p;
   for(int k=0;k<F;k++)for(int s=0;s<4;s++)q[1+4*k+s]=d[k]==0?p:quant(1./(1+exp(-(logit+strengths[s]*d[k]))));
   int ctx=j+8*min(int(code.size()),2)+24*(x.events<16?0:x.events<256?1:2)+72*x.punct;auto it=st.post.find(ctx);if(it==st.post.end())it=st.post.emplace(ctx,pri).first;auto&post=it->second;double mx=*max_element(post.begin(),post.end()),z=0,n=0;for(int m=0;m<M;m++){double a=exp(post[m]-mx);z+=a;n+=a*q[m];}int qm=clamp(int(floor(n/z+.5)),1,65535);double base=y?p:65536-p;st.baseline-=log2(base/65536);atomcost-=log2(base/65536);st.mixgain+=log2(double(y?qm:65536-qm)/base);
   for(int m=0;m<M;m++){double a=y?q[m]:65536-q[m];st.gain[m]+=log2(a/base);post[m]+=log(a/65536.);}mx=*max_element(post.begin(),post.end());for(auto&a:post)a-=mx;st.bits++;if(node>=0)node=x.tr[node].c[y];
  }
  int c=inv((unsigned char)raw[i]);if(escape){x.chars(string(1,char(c)),atomcost);escape=false;node=0;atomcost=0;}else if(code.empty()&&c==12){escape=true;node=-1;}else if(code.empty()&&c<128){if(c==7)upper=true;else if(c==64)capital=true;else if(c==6)upper=false;else {if(!(c>=65&&c<=90)&&!(c>=97&&c<=122))upper=false;if(capital||upper)c=(c-32)&255;capital=false;x.chars(string(1,char(c)),atomcost);}node=0;atomcost=0;}else{
   code.push_back(c);bool complete=code.size()==1?c<=207:code.size()==2?c<=207:true;
   if(complete){if(node<0||x.tr[node].leaf<0)throw runtime_error("code parse alignment");string s=x.w[x.tr[node].leaf];if(capital){s[0]-=32;capital=false;}if(upper)for(char&a:s)if(a>='a'&&a<='z')a-=32;x.chars(s,atomcost);code.clear();node=0;atomcost=0;}
  }
  if((i-offset)%131072==0)cerr<<"bytes="<<i-offset<<" mixture_saving="<<st.mixgain/8<<"\n";
 }
 assert(st.bits==8*(raw.size()-offset));assert(st.gain[0]==0);ofstream out(outpath);out.precision(17);out<<"{\"raw_bytes\":"<<raw.size()<<",\"unscored_prefix_bytes\":"<<offset<<",\"scored_bits\":"<<st.bits<<",\"baseline_scored_bytes\":"<<st.baseline/8<<",\"mixture_saving_bytes\":"<<st.mixgain/8<<",\"complete_ascii_dictionary_words\":"<<x.events<<",\"literal_ascii_words\":"<<x.literals<<",\"complete_pages\":"<<x.pages<<",\"article_bank\":"<<x.bank.size()<<",\"donor_selections\":"<<x.donors<<",\"bounded_rows\":"<<x.rows.size()<<",\"contexts\":"<<st.post.size()<<",\"identity_neutral\":true,\"models\":[";
 for(int k=0;k<F;k++)for(int s=0;s<4;s++){if(k||s)out<<',';out<<"{\"family\":\""<<fn[k]<<"\",\"strength\":"<<strengths[s]<<",\"saving_bytes\":"<<st.gain[1+k*4+s]/8<<'}';}out<<"],\"wall_seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-begun).count()<<",\"contract\":\"final uint16 replay, all post-sync bits including partial EOF, prefix ASCII completion, cold bank, bounded causal controls; not a native archive\"}";
}
int main(int argc,char**argv){try{if(argc!=8){cerr<<"raw final_p dictionary graph constructors limit out\n";return 2;}run(argv[1],argv[2],argv[3],argv[4],argv[5],stoull(argv[6]),argv[7]);return 0;}catch(exception&e){cerr<<e.what()<<'\n';return 1;}}
