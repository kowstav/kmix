// Exact per-token online adaptation of the transformer's output head (what a decoder can do).
// usage: headadapt prefix lr_w lr_b wd_w wd_b reset(0/1) [adam_beta2 (0=sgd)] [outloss.f32]
// logits = 15*tanh((W+dW) x + db / 15), x = xq*asc. After coding each token: SGD (or RMS-normalized SGD)
// step on dW, db with the true token. reset=1 zeroes dW,db at every piece start (pos==0).
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <immintrin.h>
#define V 205
#define D 192
static long fsz(const char*f){FILE*x=fopen(f,"rb");if(!x){perror(f);exit(1);}fseek(x,0,SEEK_END);long n=ftell(x);fclose(x);return n;}
static void* rd(const char*f,long*n){*n=fsz(f);void*p=malloc(*n);FILE*x=fopen(f,"rb");if(fread(p,1,*n,x)!=(size_t)*n){perror(f);exit(1);}fclose(x);return p;}
int main(int argc,char**argv){
  char fn[1024]; long n;
  const char*P=argv[1]; float lrw=atof(argv[2]), lrb=atof(argv[3]), wdw=atof(argv[4]), wdb=atof(argv[5]); int reset=atoi(argv[6]);
  float b2 = argc>7? atof(argv[7]) : 0.f; const char* outl = argc>8? argv[8] : NULL;
  float lr2 = argc>9? atof(argv[9]) : 0.f; int reset2 = argc>10? atoi(argv[10]) : 1;
  FILE* fdist = (argc>11 && argv[11][0]) ? fopen(argv[11],"wb") : NULL;  // adapted distributions, f16 x 205 per position
  sprintf(fn,"%s.xq",P); int8_t*xq=rd(fn,&n); long N=n/D;
  sprintf(fn,"%s.tgt",P); uint8_t*tg=rd(fn,&n);
  sprintf(fn,"%s.pos",P); int32_t*pos=rd(fn,&n);
  sprintf(fn,"%s.W",P); float*W=rd(fn,&n);
  sprintf(fn,"%s.asc",P); float*ascp=rd(fn,&n); float asc=ascp[0];
  float*dW2=calloc(V*D,4),*db2=calloc(V,4);
  float*dW=calloc(V*D,4),*db=calloc(V,4),*vW=calloc(V*D,4),*vb=calloc(V,4);
  float x[D], z[V], th[V], p[V], g[V];
  double tot=0, tot0=0; double bucket[8]={0},bucket0[8]={0}; long bn[8]={0};
  FILE*fo= outl? fopen(outl,"wb"):NULL;
  float sw=1.f, sb=1.f; // lazy decay scales: effective dW = sw*dW
  for(long t=0;t<N;t++){
    if(reset && pos[t]==0){ memset(dW,0,4*V*D); memset(db,0,4*V); sw=sb=1.f; }
    if(lr2>0 && reset2 && pos[t]==0){ memset(dW2,0,4*V*D); memset(db2,0,4*V); }
    const int8_t* q=xq+t*D; for(int i=0;i<D;i++) x[i]=q[i]*asc;
    float m=-1e30f, m0=-1e30f; float z0[V];
    for(int o=0;o<V;o++){ const float*w=W+o*D,*d=dW+o*D,*d2=dW2+o*D; float a=0,a0=0,a2=0; for(int i=0;i<D;i++){a0+=w[i]*x[i]; a+=d[i]*x[i]; a2+=d2[i]*x[i];}
      z0[o]=15.f*tanhf(a0/15.f); z[o]=a0+sw*a+sb*db[o]+a2+db2[o]; th[o]=tanhf(z[o]/15.f); z[o]=15.f*th[o]; if(z[o]>m)m=z[o]; if(z0[o]>m0)m0=z0[o]; }
    double s=0,s0=0; for(int o=0;o<V;o++){p[o]=expf(z[o]-m); s+=p[o]; s0+=exp(z0[o]-m0);}
    int y=tg[t]; double lo=-(z[y]-m-log(s)), lo0=-(z0[y]-m0-log(s0));
    tot+=lo; tot0+=lo0; int bk= pos[t]<16?0: pos[t]<64?1: pos[t]<256?2: pos[t]<1024?3: pos[t]<4096?4: pos[t]<16384?5:6;
    bucket[bk]+=lo; bucket0[bk]+=lo0; bn[bk]++;
    if(fo){float lf=(float)lo; fwrite(&lf,4,1,fo);}
    if(fdist){ unsigned short hb[V]; for(int o=0;o<V;o++) hb[o]=_cvtss_sh(p[o]/(float)s,0); fwrite(hb,2,V,fdist); }
    // gradient
    for(int o=0;o<V;o++){ float pp=p[o]/(float)s; g[o]=(pp-(o==y))*(1.f-th[o]*th[o]); }
    // decay (lazy)
    if(wdw>0){ sw*= (1.f-wdw); if(sw<1e-3f){ for(int i=0;i<V*D;i++) dW[i]*=sw; sw=1.f; } }
    if(wdb>0){ sb*= (1.f-wdb); if(sb<1e-3f){ for(int i=0;i<V;i++) db[i]*=sb; sb=1.f; } }
    if(lr2>0){ for(int o=0;o<V;o++){ float c=lr2*g[o]; float*d=dW2+o*D; for(int i=0;i<D;i++) d[i]-=c*x[i]; db2[o]-=lr2*g[o]; } }
    if(b2>0){ // RMSprop-style per-row normalization (cheap: per output row second moment)
      for(int o=0;o<V;o++){ vb[o]=b2*vb[o]+(1-b2)*g[o]*g[o]; float r=1.f/(sqrtf(vb[o])+1e-3f);
        float c=lrw*g[o]*r/sw; float*d=dW+o*D; for(int i=0;i<D;i++) d[i]-=c*x[i]; db[o]-=lrb*g[o]*r/sb; }
    } else {
      for(int o=0;o<V;o++){ float c=lrw*g[o]/sw; if(c==0)continue; float*d=dW+o*D; for(int i=0;i<D;i++) d[i]-=c*x[i]; db[o]-=lrb*g[o]/sb; }
    }
  }
  if(fo) fclose(fo);
  if(fdist) fclose(fdist);
  printf("lr2 %g reset2 %d\n",lr2,reset2);
  printf("N %ld base %.6f adapted %.6f rel %+.4f%% | lrw %g lrb %g wdw %g wdb %g reset %d b2 %g\n",N,tot0/N,tot/N,(tot/tot0-1)*100,lrw,lrb,wdw,wdb,reset,b2);
  const char*nm[7]={"<16","<64","<256","<1K","<4K","<16K",">=16K"};
  for(int k=0;k<7;k++) if(bn[k]) printf("  pos%-6s n=%9ld base %.4f adapted %.4f rel %+.3f%%\n",nm[k],bn[k],bucket0[k]/bn[k],bucket[k]/bn[k],(bucket[k]/bucket0[k]-1)*100);
  return 0;
}
