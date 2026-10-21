// Online adaptation of head + block-11 MLP down projection (float deltas), exact per token.
// usage: deepadapt prefix lr_head lr_down [rank(0=full)] [lr_lowrank]
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#define V 205
#define D 192
#define H 768
static long fsz(const char*f){FILE*x=fopen(f,"rb");if(!x){perror(f);exit(1);}fseek(x,0,SEEK_END);long n=ftell(x);fclose(x);return n;}
static void* rd(const char*f,long*n){*n=fsz(f);void*p=malloc(*n);FILE*x=fopen(f,"rb");if(fread(p,1,*n,x)!=(size_t)*n){perror(f);exit(1);}fclose(x);return p;}
int main(int argc,char**argv){
  char fn[1024]; long n; const char*P=argv[1]; float lrh=atof(argv[2]), lrd=atof(argv[3]);
  sprintf(fn,"%s.x12",P); float*X12=rd(fn,&n); long N=n/(4*D);
  sprintf(fn,"%s.hq",P); uint8_t*HQ=rd(fn,&n);
  sprintf(fn,"%s.tgt",P); uint8_t*tg=rd(fn,&n);
  sprintf(fn,"%s.pos",P); int32_t*pos=rd(fn,&n);
  sprintf(fn,"%s.Wd",P); float*Wd=rd(fn,&n);
  sprintf(fn,"%s.hsc",P); float hsc=*(float*)rd(fn,&n);
  sprintf(fn,"%s.Wu",P); float*Wu=rd(fn,&n);
  sprintf(fn,"%s.asc",P); float asc=*(float*)rd(fn,&n);
  float*dWu=calloc(V*D,4),*db=calloc(V,4),*dWd=calloc(D*H,4);
  float hf[H], x[D], nn[D], xq[D], z[V], th[V], g[V], dxq[D], dx[D];
  double tot=0, tot0=0;
  for(long t=0;t<N;t++){
    const uint8_t*hq=HQ+t*H; for(int j=0;j<H;j++) hf[j]=hq[j]*hsc;
    const float*x12=X12+t*D;
    for(int i=0;i<D;i++){ float a=0; if(lrd>0){const float*w=dWd+i*H; for(int j=0;j<H;j++) a+=w[j]*hf[j];} x[i]=x12[i]+a; }
    // base path (no deltas) for reference loss
    double ms0=0; for(int i=0;i<D;i++) ms0+=x12[i]*x12[i]; float r0=1.f/sqrtf((float)(ms0/D)+1.1920928955078125e-07f);
    double ms=0; for(int i=0;i<D;i++) ms+=x[i]*x[i]; float rr=sqrtf((float)(ms/D)+1.1920928955078125e-07f), r=1.f/rr;
    float xq0[D];
    for(int i=0;i<D;i++){ nn[i]=x[i]*r; float q=nearbyintf(nn[i]/asc); if(q>127)q=127; if(q<-128)q=-128; xq[i]=q*asc;
      float q0=nearbyintf(x12[i]*r0/asc); if(q0>127)q0=127; if(q0<-128)q0=-128; xq0[i]=q0*asc; }
    float m=-1e30f,m0=-1e30f, z0[V];
    for(int o=0;o<V;o++){ const float*w=Wu+o*D,*d=dWu+o*D; float a=0,a0=0,ad=0; for(int i=0;i<D;i++){a+=w[i]*xq[i]; ad+=d[i]*xq[i]; a0+=w[i]*xq0[i];}
      z0[o]=15.f*tanhf(a0/15.f); if(z0[o]>m0)m0=z0[o];
      float zz=a+ad+db[o]; th[o]=tanhf(zz/15.f); z[o]=15.f*th[o]; if(z[o]>m)m=z[o]; }
    double s=0,s0=0; float p[V]; for(int o=0;o<V;o++){p[o]=expf(z[o]-m); s+=p[o]; s0+=exp(z0[o]-m0);}
    int y=tg[t]; tot+=-(z[y]-m-log(s)); tot0+=-(z0[y]-m0-log(s0));
    for(int o=0;o<V;o++) g[o]=(p[o]/(float)s-(o==y))*(1.f-th[o]*th[o]);
    if(lrd>0){ // backprop to x (STE through quantization), before head update
      for(int i=0;i<D;i++) dxq[i]=0;
      for(int o=0;o<V;o++){ const float*w=Wu+o*D,*d=dWu+o*D; float go=g[o]; for(int i=0;i<D;i++) dxq[i]+=go*(w[i]+d[i]); }
      float dot=0; for(int i=0;i<D;i++) dot+=nn[i]*dxq[i];
      for(int i=0;i<D;i++) dx[i]=(dxq[i]-nn[i]*dot/D)*r;
      for(int i=0;i<D;i++){ float c=lrd*dx[i]; float*w=dWd+i*H; for(int j=0;j<H;j++) w[j]-=c*hf[j]; }
    }
    if(lrh>0) for(int o=0;o<V;o++){ float c=lrh*g[o]; float*d=dWu+o*D; for(int i=0;i<D;i++) d[i]-=c*xq[i]; db[o]-=c; }
  }
  printf("N %ld base %.6f adapted %.6f rel %+.4f%% | lr_head %g lr_down %g\n",N,tot0/N,tot/N,(tot/tot0-1)*100,lrh,lrd);
  return 0;
}
