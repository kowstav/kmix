from pathlib import Path
root=Path(__file__).resolve().parent
base=(root/'research_round8_clean_title_v4.cpp').read_text(encoding='utf-8')
struct=r'''
void clean_selftest8(string dict,string graph,string cons);
struct SemanticExpert8:CleanExpert8{
 vector<array<int,8>> semantic;uint64_t se=~0ULL,ss=~0ULL,sp=~0ULL;int sr=-1,su=-1;
 SemanticExpert8(string dict,string geom,string cons,string graph):CleanExpert8(dict,geom,cons){
  string b=readfile(graph);if(b.size()!=w.size()*16)throw runtime_error("semantic graph shape");semantic.resize(w.size());
  for(size_t i=0;i<w.size();i++)for(int k=0;k<8;k++){int v=(unsigned char)b[i*16+2*k]|((unsigned char)b[i*16+2*k+1]<<8);if(v>=int(w.size()))throw runtime_error("semantic graph bounds");semantic[i][k]=v;}
 }
 void prepare_clean(){if(se==events&&ss==serial&&sp==pages&&sr==role()&&su==punct)return;se=events;ss=serial;sp=pages;sr=role();su=punct;
  for(auto&r:current)r=Row{};
  auto addsem=[&](int target,int random,int v,int age){if(v<0)return;for(int k=0;k<8;k++){int n=semantic[v][k];current[target].add(n);current[random].add(random_word(n,age*8+k));}};
  addsem(0,1,lastcontent,0);if(lastcontent>=0)for(int n:near[lastcontent])current[4].add(n);
  for(int v:title_keys)addsem(10,11,v,0);
  int age=0;for(int i=int(recent.size())-1;i>=0&&age<16;i--)if(cls[recent[i]]==2){addsem(10,11,recent[i],++age);}
  current[8]=getrow(syntax_key(1));
  for(int k:{0,1,4,8,10,11}){mass[k].clear();for(auto[v,n]:current[k].n)for(int t:path[v])mass[k][t]+=n;}
 }
};
void semantic_selftest8(string dict,string geom,string cons,string graph){
 clean_selftest8(dict,geom,cons);SemanticExpert8 x(dict,geom,cons,graph);x.chars("<page><title>aardvark</title><text>the aardvark ",1);x.prepare_clean();
 if(x.lastcontent!=x.ids.at("aardvark")||x.current[0].total!=8||x.current[1].total!=8)throw runtime_error("semantic context selection");
 double worst=0;for(int k:{0,1,4,8,10,11}){double sum=0;for(size_t v=0;v<x.w.size();v++)sum+=x.e(k,x.path[v].back());worst=max(worst,abs(sum-1));}
 if(worst>1e-10)throw runtime_error("semantic distribution normalization");
 auto before=x.current[0].n;x.chars("uncompleted",1);x.prepare_clean();if(before!=x.current[0].n)throw runtime_error("partial word entered semantic context");
 cout<<"{\"status\":\"PASS\",\"semantic_normalization_max_error\":"<<setprecision(17)<<worst<<",\"partial_word_noninterference\":true,\"all_ids_in_bounds\":true}"<<'\n';
}
'''
base=base.replace('const array<string,6> CLEAN_ARM8=',struct+'\nconst array<string,6> CLEAN_ARM8=')
base=base.replace('{"generic","persistent_title","random_title","title_geometry","past_title_retrieval","random_past_retrieval"}', '{"generic","semantic_last_content","shuffled_last_content","spelling_last_content","semantic_topic_context","shuffled_topic_context"}')
base=base.replace('void run_clean8(string rp,string pp,string dict,string graph,string cons,size_t limit,string out)', 'void run_clean8(string rp,string pp,string dict,string graph,string cons,string semantic,size_t limit,string out)')
base=base.replace('CleanExpert8 x(dict,graph,cons);string raw=readfile(rp)', 'SemanticExpert8 x(dict,graph,cons,semantic);string raw=readfile(rp)')
needle=r'''<<g.prediction_hash<<"\"}";'''
replacement=r'''<<g.prediction_hash<<"\",\"global_mixture_saving_bytes\":"<<g.global_saving/8<<",\"fixed_candidate_saving_bytes\":[";for(int k=0;k<K8;k++){if(k)f<<',';f<<g.fixed[k]/8;}double best=-1;for(int k=0;k<K8;k++)best=max(best,g.fixed[k]-(k==0?1:log2(48.)));f<<"],\"best_fixed_after_prior_and_mode_bytes\":"<<(max(0.,best)-1)/8<<"}";'''
assert needle in base
base=base.replace(needle,replacement).replace('CLEAN_TITLE_REPLAY_NOT_ARCHIVE','FROZEN_SEMANTIC_REPLAY_NOT_ARCHIVE')
pos=base.index('int main(int argc,char**argv)')
base=base[:pos]+r'''int main(int argc,char**argv){try{if(argc==6&&string(argv[1])=="selftest"){semantic_selftest8(argv[2],argv[3],argv[4],argv[5]);return 0;}if(argc!=9)return 2;run_clean8(argv[1],argv[2],argv[3],argv[4],argv[5],argv[6],stoull(argv[7]),argv[8]);return 0;}catch(exception&e){cerr<<e.what()<<'\n';return 1;}}
'''
(root/'research_round8_semantic_replay.cpp').write_text(base,encoding='utf-8')
worker=(root/'research_round8_clean_title_v4_worker.py').read_text(encoding='utf-8')
worker=worker.replace("'clean_title_v4'","'semantic_replay_v1'").replace("'research_round8_clean_title_v4.cpp'","'research_round8_semantic_replay.cpp'").replace("'research_round8_clean_title_protocol.md'","'research_round8_semantic_protocol.md'")
worker=worker.replace("'repair':'Scientific variant: collision-free syntax/run/source-surprise namespaces. Old namespaces overlap on 224 synthetic state keys; source-surprise is not intentionally included in constructor-run. All v1-v3 evidence retained. Same candidate family and promotion threshold.'", "'scope':'Frozen pretrained semantic graph, no core retraining; paired shuffled/spelling controls; graph cost still required'")
worker=worker.replace('args=[str(P/', "m['graph']=json.loads((R/'semantic_graph_v1/manifest.json').read_text())['graph'];save()\n    args=[str(P/",1)
worker=worker.replace("str(P/'research_round7_remaining_constructors.txt')]", "str(P/'research_round7_remaining_constructors.txt'),str(R/'semantic_graph_v1/semantic_k8.u16')]")
worker=worker.replace("m['selftest']=json.loads((D/'selftest.log').read_text())", "m['selftest']=[json.loads(line) for line in (D/'selftest.log').read_text().splitlines()]")
worker=worker.replace("[('persistent_title','random_title'),('title_geometry','random_title'),('past_title_retrieval','random_past_retrieval')]", "[('semantic_last_content','shuffled_last_content'),('semantic_topic_context','shuffled_topic_context')]")
worker=worker.replace("max(p['generic'],p[random])", "max(p['generic'],p[random],p['spelling_last_content'])")
(root/'research_round8_semantic_replay_worker.py').write_text(worker,encoding='utf-8')
