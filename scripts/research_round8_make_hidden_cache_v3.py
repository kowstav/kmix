
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
s=(project_path('research_round8_hidden_cache_replay_v2.cpp', base=r)).read_text(encoding='utf-8')
s=s.replace('bool shuffle=false)const{', 'bool shuffle=false,double* best_similarity=nullptr)const{')
s=s.replace('std::array<double,256>q=prior;if(!used)return q;', 'std::array<double,256>q=prior;if(best_similarity)*best_similarity=-1;if(!used)return q;')
s=s.replace('std::array<double,256>votes{};double total=0;', 'if(best_similarity)*best_similarity=top[0].first;std::array<double,256>votes{};double total=0;')
s=s.replace('if(currentvalid){qs[0]', 'double best_fifo=-1,best_reservoir=-1;if(currentvalid){qs[0]')
s=s.replace('qs[1]=large.query(current,prior);', 'qs[1]=large.query(current,prior,false,&best_fifo);')
s=s.replace('qs[5]=longterm.query(current,prior);', 'qs[5]=longterm.query(current,prior,false,&best_reservoir);')
s=s.replace('}prefix=prefix*2+y;', '}float confidence[2]={float(std::clamp((best_fifo-.8)/.2,0.,1.)),float(std::clamp((best_reservoir-.8)/.2,0.,1.))};out.write(reinterpret_cast<char*>(confidence),8);prefix=prefix*2+y;')
s=s.replace('feature_record_bytes\\\":31', 'feature_record_bytes\\\":39')
# Independent known-identical key test also validates confidence limits.
s=s.replace('auto initial=c.query(a,prior);', 'double confidence=-2;auto initial=c.query(a,prior,false,&confidence);assert(confidence==-1);')
s=s.replace('auto predicted=c.query(a,prior);', 'auto predicted=c.query(a,prior,false,&confidence);assert(std::abs(confidence-1)<1e-12);')
(project_path('research_round8_hidden_cache_replay_v3.cpp', base=r)).write_text(s,encoding='utf-8')
f=(project_path('research_round8_hidden_cache_v2_fit_worker.py', base=r)).read_text(encoding='utf-8')
f=f.replace('research_round8_hidden_cache_replay_v2.cpp','research_round8_hidden_cache_replay_v3.cpp')
f=f.replace("('signals','<f4',(7,))", "('signals','<f4',(9,))").replace('dtype.itemsize==31','dtype.itemsize==39').replace('4096*8*31','4096*8*39')
f=f.replace("'joint_hidden_and_recency']", "'joint_hidden_and_recency','gated_fifo512','gated_shuffled_fifo512','gated_reservoir512','gated_shuffled_reservoir512','joint_gated_hidden_and_recency']")
f=f.replace('elif arm>0:cols.append', '''elif arm in [9,10,11,12]:
   source,quality={9:(1,7),10:(3,7),11:(5,8),12:(6,8)}[arm];f=records['signals'][:,source].astype(np.float64);cols.extend([f,f*records['signals'][:,quality].astype(np.float64)])
  elif arm==13:
   cols.extend(records['signals'][:,j].astype(np.float64) for j in [0,1,2,4,5]);cols.extend(records['signals'][:,a].astype(np.float64)*records['signals'][:,b].astype(np.float64) for a,b in [(1,7),(5,8)])
  elif arm>0:cols.append''')
(project_path('research_round8_hidden_cache_v3_fit_worker.py', base=r)).write_text(f,encoding='utf-8')
print('Fourteen preregistered heads: includes matched confidence gates and gated combination')
