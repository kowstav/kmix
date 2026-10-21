// Causal completed-word donor cache. Event annotations become inputs only at
// their completed delimiter; no frequency/rarity or future span is consulted.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <deque>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
struct Event { size_t lo, hi, at; std::string word; };
struct Donor { std::string bytes, word; size_t id; int preceding_role; std::array<double,26> letters{}; };
int role(const std::string& w) {
 static const std::unordered_set<std::string> function={"the","a","an","and","or","but","if","then","than","that","this","these","those","it","its","is","are","was","were","be","been","being","as","at","by","for","from","in","into","of","on","onto","to","with","without","not","no","now","there","here","i","you","he","she","we","they","which","who","when","where","why","how","all","any","each","some","such","more","most","less","very","can","could","will","would","may","might","must","do","does","did","have","has","had"};
 return w.empty()?2:(function.count(w)?1:0);
}
std::array<double,26> letters(const std::string& w) {
 std::array<double,26> a{};for(unsigned char c:w)if(c>='a'&&c<='z')a[c-'a']++;
 double s=0;for(double x:a)s+=x*x;s=std::sqrt(std::max(s,1.));for(double&x:a)x/=s;return a;
}
int main(int argc,char**argv) {
 if(argc!=4)throw std::runtime_error("input.bin events.local.tsv experts.u16");
 std::ifstream in(argv[1],std::ios::binary);std::string raw((std::istreambuf_iterator<char>(in)),{});
 std::ifstream ef(argv[2]);std::vector<Event> events;std::string line;
 while(std::getline(ef,line)){std::istringstream s(line);Event e;s>>e.lo>>e.hi>>e.at>>e.word;if(!s)continue;if(e.lo>e.hi||e.hi>e.at||e.at>raw.size())throw std::runtime_error("bad event boundary");events.push_back(e);}
 std::sort(events.begin(),events.end(),[](auto&a,auto&b){return a.at<b.at;});
 std::ofstream out(argv[3],std::ios::binary);std::deque<Donor> cache;
 std::unordered_map<std::string,std::vector<size_t>> prefixes;
 size_t cursor=0,nextid=0,active=0;std::string previous;auto prevletters=letters(previous);
 auto rebuild=[&](){prefixes.clear();for(auto&d:cache)for(size_t n=1;n<=std::min<size_t>(8,d.bytes.size()-1);n++)prefixes[d.bytes.substr(0,n)].push_back(d.id);};
 for(size_t i=0;i<raw.size();i++) {
  // A completion index equals the first prediction allowed to use this word.
  while(cursor<events.size()&&events[cursor].at<=i){auto&e=events[cursor++];std::string b=raw.substr(e.lo,e.hi-e.lo);
   if(b.size()>=1&&b.size()<=64){Donor d{b,e.word,nextid++,role(previous),letters(e.word)};cache.push_back(d);
    for(size_t n=1;n<=std::min<size_t>(8,b.size()-1);n++)prefixes[b.substr(0,n)].push_back(d.id);
    if(cache.size()>256)cache.pop_front();if(nextid%1024==0)rebuild();}
   previous=e.word;prevletters=letters(previous);
  }
  size_t used=0;std::vector<size_t> matches;
  for(size_t n=std::min<size_t>(8,i);n>0;n--){auto p=prefixes.find(raw.substr(i-n,n));if(p==prefixes.end())continue;
   for(size_t id:p->second)if(!cache.empty()&&id>=cache.front().id)matches.push_back(id);
   if(!matches.empty()){used=n;break;}}
  std::array<std::array<double,256>,8> counts{};
  for(auto&d:cache){if(used&& !std::binary_search(matches.begin(),matches.end(),d.id))continue;if(used>=d.bytes.size())continue;
   double age=double(nextid-1-d.id),sim=0.;for(int c=0;c<26;c++)sim+=prevletters[c]*d.letters[c];
   double r8=std::exp(-age/8.),r64=std::exp(-age/64.),r256=std::exp(-age/256.);
   double gram=(d.preceding_role==role(previous)?1.:.05),first=(!previous.empty()&&previous.front()==d.word.front()?1.:.05),last=(!previous.empty()&&previous.back()==d.word.back()?1.:.05);
   // Matched controls: count, recency, placement, letter bag, and combinations.
   std::array<double,8> w={1.,r8,r64,r256,r64*gram,r64*(.05+sim*sim*sim*sim),r64*first,r64*gram*(.05+sim*sim*sim*sim)*(.1+last)};
   unsigned char b=d.bytes[used];for(int law=0;law<8;law++)counts[law][b]+=w[law];
  }
  if(!cache.empty())active++;
  unsigned char actual=raw[i];uint16_t q[64];unsigned prefix=0;
  for(int bit=0;bit<8;bit++) {unsigned mask=bit?(255u<<(8-bit))&255:0;
   for(int law=0;law<8;law++){double den=.001*(256>>bit),num=.001*(128>>bit);
    for(unsigned value=0;value<256;value++)if((value&mask)==prefix){den+=counts[law][value];if(value&(128u>>bit))num+=counts[law][value];}
    q[bit*8+law]=uint16_t(std::clamp<long>(std::lround(65536*num/den),1,65535));}
   prefix|=actual&(128u>>bit);
  }
  out.write(reinterpret_cast<char*>(q),sizeof(q));
 }
 if(!out)throw std::runtime_error("output failed");
 std::cout<<"{\"bytes\":"<<raw.size()<<",\"events\":"<<events.size()<<",\"active_bytes\":"<<active<<",\"cache_capacity\":256,\"prefix_cap\":8}";
}
