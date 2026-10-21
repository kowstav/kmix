// P04 finite rendered-integer predictions, with all false alarms charged.
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <regex>
#include <string>
#include <vector>
using namespace std;
int inv(int c){if(c>=123&&c<127)c-=43;else if(c>=80&&c<84)c+=43;else if((c>=58&&c<=63)||(c>=74&&c<=79))c^=112;if(c==88||c==96)c^=56;return c;}
string read(string p){ifstream f(p,ios::binary);if(!f)throw runtime_error("missing "+p);return string(istreambuf_iterator<char>(f),{});}
const array<string,6>names={"last_number","plus_one","minus_one","linear_difference","same_field_last","page_year"};
struct State{
 long long last=0,before=0,year=0;int n=0,column=0;string digits,tail,word,key;map<string,long long>fields;
 array<string,6>candidates(){array<string,6>s;bool boundary=!tail.empty()&&string(" \t\n=|:;\"").find(tail.back())!=string::npos;if(!boundary)return s;if(n){s[0]=to_string(last);if(last<999999999999LL)s[1]=to_string(last+1);if(last>0)s[2]=to_string(last-1);if(n>1&&last+(last-before)>=0&&last+(last-before)<1000000000000LL)s[3]=to_string(last+(last-before));}auto it=fields.find(key+":"+to_string(column));if(it!=fields.end())s[4]=to_string(it->second);if(year)s[5]=to_string(year);return s;}
 void chars(string text){for(unsigned char c:text){if(c>='0'&&c<='9'){if(digits!="overflow"&&digits.size()<12)digits+=c;else digits="overflow";}else if(!digits.empty()){if(digits!="overflow"){long long v=stoll(digits);before=last;last=v;n++;if(digits.size()==4&&v>=1000&&v<=2100)year=v;if(fields.size()>=1024&&!fields.count(key+":"+to_string(column)))fields.erase(fields.begin());fields[key+":"+to_string(column)]=v;}digits.clear();}
  if((c>='a'&&c<='z')||(c>='A'&&c<='Z')){if(word.size()<32)word+=char(tolower(c));}else{if(c=='=')key=word;word.clear();}if(c=='|')column++;if(c=='\n')column=0;tail+=char(c);if(tail.size()>16)tail.erase(tail.begin());if(tail.size()>=6&&tail.substr(tail.size()-6)=="<page>"){year=0;key.clear();fields.clear();}
 }}
};
int main(int argc,char**argv){try{assert(argc==5);auto begin=chrono::steady_clock::now();string raw=read(argv[1]),ps=read(argv[2]),ds=read(argv[3]);assert(ps.size()==raw.size()*16);vector<string>w;regex rx("[a-z]+");for(sregex_iterator it(ds.begin(),ds.end(),rx),end;it!=end;++it)w.push_back(it->str());
 State st;constexpr int M=13;array<double,M>gain{},posterior;posterior.fill(-log(24.));posterior[0]=-log(2.);array<string,6>target;array<int,6>index{},alive{};int escape=0;vector<int>code;double mix=0,base=0;uint64_t bits=0,activations=0;int previous=-1;
 for(size_t i=0;i<raw.size();i++){
  // A prior boundary is known; never activate by observing the current digit.
  if(previous<0||!(previous>='0'&&previous<='9')){target=st.candidates();for(int k=0;k<6;k++){index[k]=0;alive[k]=!target[k].empty();activations+=alive[k];}}
  for(int j=0;j<8;j++){int p=(unsigned char)ps[16*i+2*j]|int((unsigned char)ps[16*i+2*j+1])<<8;int y=((unsigned char)raw[i]>>(7-j))&1;array<int,M>q;q[0]=p;
   for(int k=0;k<6;k++){double e=double(p)/65536;bool on=alive[k]&&index[k]<int(target[k].size());if(on)e=(unsigned char)target[k][index[k]]>>(7-j)&1;for(int a=0;a<2;a++){double weight=a?.1:.01;q[1+2*k+a]=on?clamp(int(floor(((1-weight)*p/65536.+weight*e)*65536+.5)),1,65535):p;}}
   double z=0,a=0,mx=*max_element(posterior.begin(),posterior.end());for(int m=0;m<M;m++){double v=exp(posterior[m]-mx);z+=v;a+=v*q[m];}int qp=clamp(int(floor(a/z+.5)),1,65535);double old=y?p:65536-p;mix+=log2(double(y?qp:65536-qp)/old);base-=log2(old/65536.);for(int m=0;m<M;m++){double prob=y?q[m]:65536-q[m];gain[m]+=log2(prob/old);posterior[m]+=log(prob/65536.);}mx=*max_element(posterior.begin(),posterior.end());for(auto&v:posterior)v-=mx;bits++;
   for(int k=0;k<6;k++)if(alive[k]&&index[k]<int(target[k].size())&&int((unsigned char)target[k][index[k]]>>(7-j)&1)!=y)alive[k]=0;
  }
  for(int k=0;k<6;k++)if(alive[k])index[k]++;
  int c=inv((unsigned char)raw[i]);if(escape){st.chars(string(1,char(c)));escape=0;}else if(code.empty()&&c==12)escape=1;else if(code.empty()&&c<128){if(c!=7&&c!=64&&c!=6)st.chars(string(1,char(c)));}else{code.push_back(c);bool complete=code.size()==1?c<=207:code.size()==2?c<=207:true;if(complete){int v=code.size()==1?code[0]-128:code.size()==2?80+(code[0]-208)*80+code[1]-128:3920+((code[0]-240)*32+code[1]-208)*80+code[2]-128;if(v>=0&&v<int(w.size()))st.chars(w[v]);code.clear();}}
  previous=c;
 }
 assert(bits==raw.size()*8&&gain[0]==0);ofstream out(argv[4]);out.precision(17);out<<"{\"raw_bytes\":"<<raw.size()<<",\"scored_bits\":"<<bits<<",\"mixture_saving_bytes\":"<<mix/8<<",\"baseline_bytes\":"<<base/8<<",\"candidate_activations\":"<<activations<<",\"models\":[";for(int k=0;k<6;k++)for(int a=0;a<2;a++){if(k||a)out<<',';out<<"{\"program\":\""<<names[k]<<"\",\"copy_weight\":"<<(a?.1:.01)<<",\"saving_bytes\":"<<gain[1+2*k+a]/8<<'}';}out<<"],\"wall_seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-begin).count()<<",\"contract\":\"all final integer bits; candidate selected using known prefix; finite literal integer programs; not native archive\"}";
 return 0;}catch(exception&e){cerr<<e.what()<<'\n';return 1;}}
