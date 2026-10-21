// Reads dense float16 prior rows (V=205 per token) from argv[1] (FIFO or file) and writes
// argv[2].cnt (u8 per token), argv[2].idx (u8 per entry), argv[2].val (f16 per entry).
// Keeps entries with value >= threshold argv[3] (default 0.0007 ~= 0.25 * prior act scale 0.002766).
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static float h2f(uint16_t h){uint32_t s=(h&0x8000)<<16,e=(h>>10)&31,m=h&0x3ff,x;
 if(e==0){ if(!m) x=s; else { int k=0; while(!(m&0x400)){m<<=1;k++;} m&=0x3ff; x=s|((112-k)<<23)|(m<<13);} }
 else if(e==31) x=s|0x7f800000|(m<<13); else x=s|((e+112)<<23)|(m<<13);
 float f; memcpy(&f,&x,4); return f;}
int main(int argc,char**argv){
  const int V=205; float thr = argc>3? atof(argv[3]) : 0.0007f;
  char fn[1024];
  FILE*in=fopen(argv[1],"rb");
  snprintf(fn,sizeof fn,"%s.cnt",argv[2]); FILE*oc=fopen(fn,"wb");
  snprintf(fn,sizeof fn,"%s.idx",argv[2]); FILE*oi=fopen(fn,"wb");
  snprintf(fn,sizeof fn,"%s.val",argv[2]); FILE*ov=fopen(fn,"wb");
  if(!in||!oc||!oi||!ov){fprintf(stderr,"open fail\n");return 1;}
  setvbuf(in,NULL,_IOFBF,1<<24); setvbuf(oc,NULL,_IOFBF,1<<22); setvbuf(oi,NULL,_IOFBF,1<<22); setvbuf(ov,NULL,_IOFBF,1<<23);
  uint16_t row[205]; unsigned char ib[205]; uint16_t vb[205];
  unsigned long long ntok=0, nent=0; int maxn=0;
  while(fread(row,2,V,in)==(size_t)V){
    int n=0;
    for(int i=0;i<V;i++){ if(h2f(row[i])>=thr){ ib[n]=(unsigned char)i; vb[n]=row[i]; n++; } }
    if(n>255){fprintf(stderr,"n>255\n");return 2;}
    unsigned char c=(unsigned char)n; fwrite(&c,1,1,oc); fwrite(ib,1,n,oi); fwrite(vb,2,n,ov);
    ntok++; nent+=n; if(n>maxn)maxn=n;
    if((ntok & ((1ULL<<24)-1))==0) {fprintf(stderr,"tok %llu avg %.2f\n",ntok,(double)nent/ntok); fflush(stderr);}
  }
  fclose(oc); fclose(oi); fclose(ov);
  fprintf(stderr,"DONE tokens %llu entries %llu avg %.2f max %d\n",ntok,nent,(double)nent/ntok,maxn);
  return 0;
}
