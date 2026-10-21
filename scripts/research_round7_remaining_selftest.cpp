#define main replay_program_main
#include "research_round7_remaining_experts.cpp"
#undef main
int main(int argc,char**argv){assert(argc==4);Expert x(argv[1],argv[2],argv[3]);
 double worst=0;auto check=[&](){x.prepare();for(int k=0;k<F;k++){double z=0;for(size_t j=0;j<x.w.size();j++)z+=x.e(k,x.path[j].back());worst=max(worst,abs(z-1));assert(abs(z-1)<1e-10);}
  for(int v:{0,79,80,3919,3920,44514}){double gp=1;array<double,F>ep;ep.fill(1);for(size_t i=0;i+1<x.path[v].size();i++){int n=x.path[v][i],to=x.path[v][i+1],a=x.tr[n].c[0],b=x.tr[n].c[1];double ga=x.g(a),gb=x.g(b);gp*=to==a?ga/(ga+gb):gb/(ga+gb);for(int k=0;k<F;k++){double ea=x.e(k,a),eb=x.e(k,b);if(ea+eb>0)ep[k]*=to==a?ea/(ea+eb):eb/(ea+eb);else ep[k]=0;}}
   assert(abs(gp-x.g(x.path[v].back()))<1e-12);for(int k=0;k<F;k++)assert(abs(ep[k]-x.e(k,x.path[v].back()))<1e-10);
  }};
 check();x.page_start();for(int i=0;i<12;i++)x.chars("the aardvark and a aardvark. ",10);check();assert(x.bank.empty());x.chars("<title>aardvark</title> the aardvark </page>",10);assert(x.bank.size()==1);x.page_start();x.chars("<title>aardvark</title> ",10);x.prepare();assert(x.current[10].total>0);check();
 auto old=x.literals;x.chars("i ",2);if(!x.ids.count("i"))assert(x.literals==old+1);check();x.chars("uncompleted",3);auto events=x.events;x.prepare();assert(x.events==events);x.chars(" ",1);assert(x.events==events||x.events==events+1);
 cout<<"{\"normalization\":\"PASS\",\"max_error\":"<<worst<<",\"tree_mass_telescope\":true,\"completed_past_article_only\":true,\"literal_i_completion\":true,\"prefix_only_word_updates\":true}"<<endl;
}
