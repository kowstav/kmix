#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <vector>
#include <unordered_map>
#include <fstream>
#include <algorithm>
#include "dictionary.h"
// Full native decode from the stream start. Provenance labels are supervision
// only: they never enter predictor inputs or decoder-side decisions.
static int inv(int c){if(c>='{'&&c<127)c+='P'-'{';else if(c>='P'&&c<'T')c-='P'-'{';else if((c>=':'&&c<='?')||(c>='J'&&c<='O'))c^=0x70;if(c=='X'||c=='`')c^='X'^'`';return c;}
static bool alpha(int c){return (c>='a'&&c<='z')||(c>='A'&&c<='Z');}
static std::vector<int> code(int j){if(j<80)return{128+j};if(j<3920){j-=80;return{208+j/80,128+j%80};}j-=3920;return{240+(j/80)/32,208+(j/80)%32,128+j%80};}
int main(int argc,char**argv){
 if(argc!=6)return 10;
 FILE*in=fopen(argv[1],"rb"),*reference=fopen(argv[1],"rb"),*df=fopen(argv[2],"rb"),*out=fopen(argv[3],"wb"),*sample=fopen(argv[4],"wb");if(!in||!reference||!df||!out||!sample)return 11;
 preprocessor::Dictionary native(df,false,true);fclose(df);
 std::ifstream dictfile(argv[2]);std::string line;std::vector<std::string>words;
 while(std::getline(dictfile,line)){std::string w;for(char c:line)if(c>='a'&&c<='z')w+=c;else if(!w.empty()){words.push_back(w);w.clear();}if(!w.empty())words.push_back(w);}
 if(words.size()!=44515)return 12;std::unordered_map<uint32_t,std::string>map;
 for(int j=0;j<(int)words.size();j++){auto v=code(j);uint32_t key=0;for(size_t k=0;k<v.size();k++)key|=uint32_t(v[k])<<(8*k);map[key]=words[j];}
 uint64_t limit=strtoull(argv[5],nullptr,10),decoded=0,wordcount=0,checked=0;uint32_t remaining=0;int type=0,flag=0;bool upper=false,capital=false,intext=false,tag=false;std::string tagbuf,word;uint64_t wordlo=0,wordhi=0,pending=UINT64_MAX;bool wordtext=false,quote=false;uint64_t quotehi=0;
 auto flush=[&](){if(!word.empty()){fprintf(out,"%llu\t%llu\t%d\t%s\n",(unsigned long long)wordlo,(unsigned long long)wordhi,wordtext,word.c_str());wordcount++;}word.clear();quote=false;};
 while((uint64_t)ftell(in)<limit){
  if(!remaining){flush();int a=getc(in);if(a==EOF)break;type=a;int rtype=getc(reference);if(rtype!=type)return 13;uint32_t len=0,rlen=0;for(int k=0;k<4;k++){int b=getc(in),rb=getc(reference);if(b<0||b!=rb)return 14;len=(len<<8)|b;rlen=(rlen<<8)|rb;}remaining=len;if(type==7){flag=getc(in);if(flag!=getc(reference))return 15;}else flag=0;pending=UINT64_MAX;}
  uint64_t lo=ftell(in);int c=getc(in);if(c==EOF)break;std::string expansion;
  if(type==7&&flag){c=inv(c);
   if(c==12){upper=false;int e=getc(in);if(e<0)return 16;expansion+=(char)inv(e);}
   else if(c==7){upper=true;if(pending==UINT64_MAX)pending=lo;continue;}
   else if(c==64){capital=true;if(pending==UINT64_MAX)pending=lo;continue;}
   else if(c==6){upper=false;if(pending==UINT64_MAX)pending=lo;continue;}
   else if(c>=128){uint32_t key=c;if(c>207){int e=getc(in);if(e<0)return 17;c=inv(e);key|=c<<8;if(c>207){e=getc(in);if(e<0)return 18;key|=inv(e)<<16;}}auto it=map.find(key);if(it==map.end())return 19;expansion=it->second;for(size_t j=0;j<expansion.size();j++){if((j==0&&capital)||upper)expansion[j]=expansion[j]-'a'+'A';if(j==0&&capital)capital=false;}}
   else{if(!alpha(c))upper=false;if(capital||upper)c=(c-'a')+'A';capital=false;expansion+=(char)c;}
  }else expansion+=(char)c;
  uint64_t hi=ftell(in);if(pending!=UINT64_MAX){lo=pending;pending=UINT64_MAX;}
  if(expansion.size()>remaining)return 20;
  for(unsigned char ch:expansion){int ref=(type==7&&flag)?native.Decode(reference):getc(reference);if(ref!=(int)ch)return 21;checked++;decoded++;if(decoded<=8192)putc(ch,sample);
   if(ch=='<'){tag=true;tagbuf="<";}
   else if(tag){tagbuf+=(char)ch;if(ch=='>'){if(tagbuf.rfind("<text",0)==0)intext=true;else if(tagbuf=="</text>"||tagbuf=="</page>"||tagbuf=="</revision>")intext=false;tag=false;}else if(tagbuf.size()>2048)tag=false;}
   if(alpha(ch)){if(word.empty()){wordlo=lo;wordtext=intext&&!tag;}if(quote){word+='\'';quote=false;}word+=(char)((ch>='A'&&ch<='Z')?ch-'A'+'a':ch);wordhi=hi;}
   else if(ch=='\''&&!word.empty()&&!quote){quote=true;quotehi=hi;}
   else flush();
  }
  remaining-=expansion.size();
  // Both independent native and annotated decoders must consume the same bytes
  // at each atom boundary, including suffix/prefix expansions and controls.
  if(ftell(in)!=ftell(reference))return 22;
 }
 // Deliberately leave a word crossing the requested terminal cutoff unlabelled.
 fclose(in);fclose(reference);fclose(out);fclose(sample);fprintf(stdout,"{\"decoded_bytes_checked\":%llu,\"word_events\":%llu,\"native_byte_comparison\":\"PASS\"}\n",(unsigned long long)checked,(unsigned long long)wordcount);return 0;
}
