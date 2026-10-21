from pathlib import Path
import py_compile
R=Path(__file__).resolve().parent
base=(R/'research_round8_clean_title_v4.cpp').read_text(encoding='utf-8')
base=base[:base.index('const array<string,6> CLEAN_ARM8=')]
struct=r'''
struct DirectedRow8{int source=-1;array<int,8>target{};array<uint16_t,8>count{};
 void add(int key,int v,unsigned amount){if(source!=key){source=key;count.fill(0);}int chosen=-1;for(int i=0;i<8;i++)if(count[i]&&target[i]==v)chosen=i;if(chosen<0)for(int i=0;i<8;i++)if(!count[i]){chosen=i;target[i]=v;break;}if(chosen<0){chosen=0;for(int i=1;i<8;i++)if(count[i]<count[chosen]||(count[i]==count[chosen]&&target[i]<target[chosen]))chosen=i;target[chosen]=v;}if(unsigned(count[chosen])+amount>65535)for(auto&c:count)c=(unsigned(c)+1)/2;count[chosen]+=amount;}
};
struct DirectedExpert8:CleanExpert8{
 array<DirectedRow8,1024>next,wide;vector<int>pending;uint64_t de=~0ULL,ds=~0ULL,dp=~0ULL;int dr=-1,du=-1;
 using CleanExpert8::CleanExpert8;
 int random_word(int v,int salt)const{int lo=(v/256)*256,hi=min(int(w.size()),lo+256);vector<int>pool;for(int j=lo;j<hi;j++)if(w[j].size()==w[v].size()&&cls[j]==cls[v])pool.push_back(j);if(pool.empty())return v;return pool[(uint32_t(v)*2654435761u+uint32_t(salt)*2246822519u)%pool.size()];}
 static size_t slot(int v){return (uint32_t(v)*2654435761u)&1023;}
 void learned(int v){if(cls[v]!=2)return;if(!pending.empty())next[slot(pending.back())].add(pending.back(),v,1);int age=0;for(int i=int(pending.size())-1;i>=0&&age<8;i--,age++)wide[slot(pending[i])].add(pending[i],v,8-age);pending.push_back(v);if(pending.size()>8)pending.erase(pending.begin());}
 void chars(const string&s,double cost){for(char c:s){uint64_t previous=events,pp=pages;CleanExpert8::chars(string(1,c),cost/max(size_t(1),s.size()));if(pages!=pp)pending.clear();if(events!=previous){if(events!=previous+1||recent.empty())throw runtime_error("directed commit accounting");learned(recent.back());}}}
 void prepare_clean(){if(de==events&&ds==serial&&dp==pages&&dr==role()&&du==punct)return;de=events;ds=serial;dp=pages;dr=role();du=punct;for(auto&r:current)r=Row{};
  auto add=[&](int a,int b,const DirectedRow8&r){if(r.source!=lastcontent)return;for(int i=0;i<8;i++)if(r.count[i]){current[a].add(r.target[i],r.count[i]);current[b].add(random_word(r.target[i],i),r.count[i]);}};
  if(lastcontent>=0){add(0,1,next[slot(lastcontent)]);add(10,11,wide[slot(lastcontent)]);}int age=0;for(int i=int(recent.size())-1;i>=0&&age<16;i--)if(cls[recent[i]]==2){current[4].add(recent[i]);age++;}current[8]=getrow(syntax_key(1));
  for(int k:{0,1,4,8,10,11}){mass[k].clear();for(auto[v,n]:current[k].n)for(int t:path[v])mass[k][t]+=n;}
 }
};
void directed_selftest8(string dict,string graph,string cons){
 DirectedExpert8 x(dict,graph,cons);x.chars("<page><title>aardvark</title><text>aardvark zebra aardvark zebra aardvark ",1);x.prepare_clean();int a=x.ids.at("aardvark"),z=x.ids.at("zebra");auto&r=x.next[x.slot(a)];bool found=false;for(int i=0;i<8;i++)found|=r.count[i]&&r.target[i]==z;if(r.source!=a||!found)throw runtime_error("directed pair not learned");auto old=x.current[0].n;x.chars("uncompleted",1);x.prepare_clean();if(old!=x.current[0].n)throw runtime_error("unfinished word entered memory");double worst=0;for(int k:{0,1,4,8,10,11}){double sum=0;for(size_t v=0;v<x.w.size();v++)sum+=x.e(k,x.path[v].back());worst=max(worst,abs(sum-1));}if(worst>1e-10)throw runtime_error("directed normalization");
 x.chars("</text></page><page><title>",1);if(!x.pending.empty())throw runtime_error("article pending sources not reset");DirectedRow8 q;for(int i=0;i<200000;i++)q.add(1,i%17,8);for(auto c:q.count)if(c>65535)throw runtime_error("counter overflow");q.add(2,3,1);if(q.source!=2||q.count[0]!=1)throw runtime_error("row collision replacement");
 cout<<"{\"status\":\"PASS\",\"pair_learning\":true,\"unfinished_word_noninterference\":true,\"article_pending_reset\":true,\"normalization_error\":"<<setprecision(17)<<worst<<",\"counter_and_collision_checks\":true,\"packed_two_model_row_bytes_design\":69632,\"instrumented_two_row_arrays_bytes\":"<<2*sizeof(x.next)<<"}"<<'\n';
}
'''
(R/'research_round8_directed_memory_library.h').write_text(base+struct,encoding='utf-8')
s=(R/'research_round8_warm_source.cpp').read_text(encoding='utf-8').replace('research_round8_clean_title_library.h','research_round8_directed_memory_library.h').replace('CleanExpert8','DirectedExpert8')
s=s.replace('array<Gate8,6>gates;', 'ofstream features(out+"."+qy.name+".features",ios::binary);uint64_t exported_bits=0;')
begin=s.index('    array<pair<double,double>,6>sig=');end=s.index('if(predictive_node>=0)predictive_node=x.tr[predictive_node].c[y];',begin)
s=s[:begin]+r'''    uint16_t pp=p;uint8_t yy=y;features.write(reinterpret_cast<char*>(&pp),2);features.write(reinterpret_cast<char*>(&yy),1);for(int k:{0,1,4,10,11,8}){float v=prose?d[k]:0;features.write(reinterpret_cast<char*>(&v),4);}exported_bits++;double base=(y?p:65536-p)/65536.;bytecost-=log2(base);
    '''+s[end:]
begin=s.index('  for(int a=0;a<6;a++){auto&g=gates[a];');end=s.index('\n }',begin)
s=s[:begin]+r'''  if(exported_bits!=8*(raw.size()-offset))throw runtime_error("directed feature bit accounting");features.close();f<<"],\"exported_bits\":"<<exported_bits<<",\"record_bytes\":27}";f.flush();cerr<<"completed="<<qy.name<<" prefix_seen="<<seen<<" past_events="<<before<<"\n";'''+s[end:]
s=s.replace('if(argc!=7)return 2;', 'if(argc==5&&string(argv[1])=="selftest"){directed_selftest8(argv[2],argv[3],argv[4]);return 0;}if(argc!=7)return 2;').replace('WARM_SOURCE_COLD_CORE_CONDITIONAL_DIAGNOSTIC','DIRECTED_WARM_SOURCE_COLD_CORE_DIAGNOSTIC')
(R/'research_round8_directed_memory_export.cpp').write_text(s,encoding='utf-8')
worker=(R/'research_round8_continuous_v2_worker.py').read_text(encoding='utf-8').replace('continuous_strength_v2','directed_memory_v1').replace('research_round8_continuous_export.cpp','research_round8_directed_memory_export.cpp').replace('research_round8_continuous_protocol.md','research_round8_directed_memory_protocol.md')
begin=worker.index(' args=[str(P/');end=worker.index(" m['status']='FITTING_CONTINUOUS_HEADS'",begin)
replacement=''' args=[str(P/'preserved/gen/.dict'),str(P/'research_round7_remaining_graph.txt'),str(P/'research_round7_remaining_constructors.txt')]
 m['parser_selftest_runtime']=run([str(binary),'selftest',*args],D/'selftest.log');m['parser_selftest']=[json.loads(s) for s in (D/'selftest.log').read_text().splitlines()];save()
 output=D/'warm.json';m['warm_export_runtime']=run([str(binary),str(P/'full_stream_regen_v2/full_ready.wrt'),*args,str(P),str(output)],D/'warm.log');warm=json.loads(output.read_text());m['warm_export']=warm;save();byname={q['slice'][0]:q for q in warm['queries']}
 dtype=np.dtype([('p','<u2'),('y','u1'),('signals','<f4',(6,))]);assert dtype.itemsize==27;slices=[]
 for s in 'abcd':
  row=byname[s];path=pathlib.Path(str(output)+'.'+s+'.features');records=np.fromfile(path,dtype=dtype);assert len(records)==row['exported_bits'];assert ((records['p']>=1)&(records['y']<=1)).all() and np.isfinite(records['signals']).all();assert np.array_equal(identity_probability(records['p'].astype(np.float64)),records['p']);row.update(feature_bytes=path.stat().st_size,feature_sha256=hashlib.sha256(path.read_bytes()).hexdigest());slices.append(records);m.setdefault('exports',[]).append(row);save()
'''
worker=worker[:begin]+replacement+worker[end:]
worker=worker.replace("['generic','semantic_last_content','shuffled_last_content','spelling_last_content','semantic_topic_context','shuffled_topic_context']", "['generic','directed_next_content','shuffled_next_content','exact_content_echo','directed_window8','shuffled_window8']")
worker=worker.replace('COMPLETE_FINITE_CONTINUOUS_DIAGNOSTIC','COMPLETE_FINITE_DIRECTED_WARM_DIAGNOSTIC')
worker=worker.replace("['research_round8_directed_memory_export.cpp','research_round8_clean_library.h'", "['research_round8_directed_memory_export.cpp','research_round8_directed_memory_library.h','research_round8_clean_library.h'")
(R/'research_round8_directed_memory_worker.py').write_text(worker,encoding='utf-8');py_compile.compile(str(R/'research_round8_directed_memory_worker.py'),doraise=True)
launcher=(R/'research_round8_continuous_v2_launch.py').read_text(encoding='utf-8').replace('continuous_strength_v2','directed_memory_v1').replace('research_round8_continuous_v2_worker.py','research_round8_directed_memory_worker.py')
(R/'research_round8_directed_memory_launch.py').write_text(launcher,encoding='utf-8');py_compile.compile(str(R/'research_round8_directed_memory_launch.py'),doraise=True)
print('PASS: directed source/export and syntax-checked worker/launcher generated')
