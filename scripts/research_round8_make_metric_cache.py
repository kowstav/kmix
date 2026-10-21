
# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
r=project_root(__file__)
base=(project_path('research_round8_hidden_cache_replay_v3.cpp', base=r)).read_text(encoding='utf-8');base=base[:base.index('int main(')]
body=r'''
struct Stats {uint64_t n=0;std::array<double,FULL> mean{},m2{};void add(const Key&k){n++;for(int j=0;j<FULL;j++){double d=k[j]-mean[j];mean[j]+=d/n;m2[j]+=d*(k[j]-mean[j]);}}};
using Top=std::array<std::pair<double,int>,8>;
static Top retrieve(const Cache&c,const Key&k,const Stats&s,int metric){
 Top top;for(auto&v:top)v={-2,-1};int used=0;double qnorm=0;std::array<double,FULL>a{},w{},mu{};
 for(int j=0;j<FULL;j++){mu[j]=metric&&s.n>=16?s.mean[j]:0;w[j]=metric==2&&s.n>=16?1/(s.m2[j]/(s.n-1)+1):1;a[j]=k[j]-mu[j];qnorm+=a[j]*a[j]*w[j];}if(qnorm<1e-12)return top;
 for(int i=0;i<c.used;i++){double dot=0,rnorm=0;for(int j=0;j<FULL;j++){double b=c.rows[i].key[j]-mu[j];dot+=a[j]*b*w[j];rnorm+=b*b*w[j];}if(rnorm<1e-12)continue;double sim=std::clamp(dot/std::sqrt(qnorm*rnorm),-1.,1.);int at=std::min(used,7);if(used>=8&&(sim<top[7].first||(sim==top[7].first&&i>top[7].second)))continue;while(at>0&&(sim>top[at-1].first||(sim==top[at-1].first&&i<top[at-1].second))){if(at<8)top[at]=top[at-1];at--;}top[at]={sim,i};used=std::min(used+1,8);}return top;
}
struct Spec {int bank,metric,k;double tau,alpha;bool shuffled;};
const std::array<Spec,17> SPECS={{{0,0,8,10,.5,false},{0,0,1,1000,.99,false},{0,0,8,1000,.99,false},{0,0,8,100,.5,false},{0,1,1,1000,.99,false},{0,1,8,1000,.99,false},{0,2,1,1000,.99,false},{0,2,8,1000,.99,false},{0,0,1,1000,.99,true},{0,1,1,1000,.99,true},{0,2,1,1000,.99,true},{1,1,1,1000,.99,false},{1,1,8,1000,.99,false},{1,1,1,1000,.99,true},{1,2,1,1000,.99,false},{1,2,8,1000,.99,false},{1,2,1,1000,.99,true}}};
static std::array<double,256> law(const Cache&c,const Top&top,const Spec&sp,const std::array<double,256>&prior){
 if(top[0].second<0)return prior;std::array<double,256>q{},v{};double sum=0;for(int j=0;j<sp.k&&top[j].second>=0;j++){int i=top[j].second;if(sp.shuffled)i=c.permutations.at(c.used).at(i);double z=std::exp(sp.tau*(top[j].first-top[0].first));v[c.rows[i].target]+=z;sum+=z;}for(int b=0;b<256;b++)q[b]=(1-sp.alpha)*prior[b]+sp.alpha*v[b]/sum;return q;
}
static void metrictest(){selftest();Key a{},b{};for(int j=0;j<FULL;j++){a[j]=j%59-29;b[j]=j%41-20;}Cache c(3,FULL,true);c.update(a,61);c.update(b,77);Stats s;auto raw=retrieve(c,a,s,0);assert(raw[0].second==0&&std::abs(raw[0].first-1)<1e-12);assert(raw==retrieve(c,a,s,1));for(int i=0;i<50;i++)s.add(i&1?a:b);for(int m=0;m<3;m++){auto top=retrieve(c,a,s,m);assert(top[0].second==0&&std::abs(top[0].first-1)<1e-12);std::array<double,256>prior{};prior.fill(1./256);for(auto sp:SPECS){auto q=law(c,top,sp,prior);assert(std::abs(std::accumulate(q.begin(),q.end(),0.)-1)<1e-12);for(int target=0;target<256;target++){int pre=0;double p=1;for(int j=0;j<8;j++){double v=prefix_p(q,pre,j);int y=(target>>(7-j))&1;p*=y?v:1-v;pre=pre*2+y;}assert(std::abs(p-q[target])<1e-12);}}}std::printf("{\"metric_selftest\":\"PASS\",\"causal_center_whiten\":true,\"all_kernel_byte_prefix_laws\":true}\n");}
int main(int argc,char**argv){try{if(argc==2&&std::string(argv[1])=="selftest"){metrictest();return 0;}if(argc!=6)throw std::runtime_error("raw finalp hidden output limit");std::ifstream raw(argv[1],std::ios::binary),pf(argv[2],std::ios::binary),hf(argv[3],std::ios::binary);std::ofstream out(argv[4],std::ios::binary);if(!raw||!pf||!hf||!out)throw std::runtime_error("open failed");int limit=std::stoi(argv[5]);Cache normal(512,FULL,true),hard(512,FULL,true);Stats stats;Key current{};bool valid=false;std::array<uint64_t,256>count{};uint64_t n=0,queries=0,hardinserts=0;
 while(n<uint64_t(limit)){unsigned char target;if(!raw.read(reinterpret_cast<char*>(&target),1))break;unsigned char hidden[193];if(!hf.read(reinterpret_cast<char*>(hidden),193))throw std::runtime_error("short hidden");std::array<double,256>prior{};for(int b=0;b<256;b++)prior[b]=(count[b]+.5)/(n+128.);std::array<Top,6>tops;
 for(auto&t:tops)for(auto&v:t)v={-2,-1};if(valid){for(int m=0;m<3;m++){tops[m]=retrieve(normal,current,stats,m);tops[3+m]=retrieve(hard,current,stats,m);}queries++;}
 std::array<std::array<double,257>,17> cdf{};for(int a=0;a<17;a++){const auto&sp=SPECS[a];auto q=law(sp.bank?hard:normal,tops[sp.bank*3+sp.metric],sp,prior);for(int b=0;b<256;b++)cdf[a][b+1]=cdf[a][b]+q[b];}
 double bytecost=0;int prefix=0;
 for(int bit=0;bit<8;bit++){unsigned char le[2];if(!pf.read(reinterpret_cast<char*>(le),2))throw std::runtime_error("short probability trace");uint16_t p=le[0]+uint16_t(le[1])*256;if(!p)throw std::runtime_error("invalid p");uint8_t y=(target>>(7-bit))&1;out.write(reinterpret_cast<char*>(le),2);out.write(reinterpret_cast<char*>(&y),1);double l=ell(double(p)/65536);bytecost-=std::log2((y?p:65536-p)/65536.);int low=prefix<<(8-bit),high=low+(1<<(8-bit)),mid=(low+high)/2;
  for(int a=0;a<17;a++){double total=cdf[a][high]-cdf[a][low],one=cdf[a][high]-cdf[a][mid];double q=std::clamp(one/total,1e-9,1-1e-9);float f=valid?float(std::clamp(ell(q)-l,-12.,12.)):0;out.write(reinterpret_cast<char*>(&f),4);}prefix=prefix*2+y;
 }
 // Hard-memory retention uses observed loss only after the target completes.
 if(valid){normal.update(current,target);if(bytecost>2){hard.update(current,target);hardinserts++;}stats.add(current);}count[target]++;valid=hidden[0];for(int j=0;j<FULL;j++)current[j]=valid?int(hidden[j+1])-128:0;n++;
 }
 out.close();if(!out)throw std::runtime_error("output failed");std::printf("{\"bytes\":%llu,\"valid_queries\":%llu,\"hard_retained_events\":%llu,\"feature_record_bytes\":71,\"kernel_families\":17,\"metric_stats_bytes\":%zu}\n",(unsigned long long)n,(unsigned long long)queries,(unsigned long long)hardinserts,sizeof(stats));return 0;
}catch(const std::exception&e){std::fprintf(stderr,"%s\n",e.what());return 1;}}
'''
(project_path('research_round8_metric_cache.cpp', base=r)).write_text(base+body,encoding='utf-8');print('Generated 17 normalized kernel/geometry/retention sources')
