
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

import itertools,json
from pathlib import Path
R=project_root(__file__)
def old(kind,prev,punct,run=0,group=0,surprise=0,rank=0):
    k=(kind+1)*4+prev;k=k*4+punct
    if kind==1:k=(k*5+run)*8+group
    if kind==2:k=(k*4+surprise)*8+rank
    return k
def new(kind,prev,punct,run=0,group=0,surprise=0,rank=0):
    k=((kind+1)<<24)|(prev<<20)|(punct<<18)
    if kind==1:k|=(run<<15)|(group<<12)
    if kind==2:k|=(surprise<<10)|rank
    return k
spaces=[[(p,u,0,0,0,0) for p,u in itertools.product(range(3),range(4))],[(p,u,r,g,0,0) for p,u,r,g in itertools.product(range(3),range(4),range(5),range(8))],[(p,u,0,0,s,r) for p,u,s,r in itertools.product(range(3),range(4),range(4),range(8))]]
before=[{old(k,*v) for v in values} for k,values in enumerate(spaces)];after=[{new(k,*v) for v in values} for k,values in enumerate(spaces)]
assert old(1,2,0,0,0)==old(2,0,2,0,0,0,0)==1600
assert len(set.union(*after))==sum(map(len,after))==876
source=(project_path('research_round7_remaining_experts.cpp', base=R)).read_text(encoding='utf-8')
a='uint64_t k=kind+1; k=k*4+(prev<0?0:cls[prev]);k=k*4+punct;if(kind==1){k=k*5+min(run,4);k=k*8+(lastcontent<0?0:min(lastcontent/6000,7));}if(kind==2){k=k*4+surprise;k=k*8+(prev<0?0:min(prev/6000,7));}return k;'
b='uint64_t k=(uint64_t(kind+1)<<24)|(uint64_t(prev<0?0:cls[prev])<<20)|(uint64_t(punct)<<18);if(kind==1)k|=(uint64_t(min(run,4))<<15)|(uint64_t(lastcontent<0?0:min(lastcontent/6000,7))<<12);if(kind==2)k|=(uint64_t(surprise)<<10)|uint64_t(prev<0?0:min(prev/6000,7));return k;'
assert source.count(a)==1
(project_path('research_round8_observer_separated.h', base=R)).write_text(source.replace(a,b),encoding='utf-8')
lib=(project_path('research_round8_conditional_library.h', base=R)).read_text(encoding='utf-8').replace('research_round7_remaining_experts.cpp','research_round8_observer_separated.h')
(project_path('research_round8_clean_library.h', base=R)).write_text(lib,encoding='utf-8')
cpp=(project_path('research_round8_clean_title_v3.cpp', base=R)).read_text(encoding='utf-8').replace('research_round8_conditional_library.h','research_round8_clean_library.h')
cpp=cpp.replace('if(x.counts[x.ids.at("aardvark")]!=3)', 'if(x.counts[x.ids.at("aardvark")]!=3)')
(project_path('research_round8_clean_title_v4.cpp', base=R)).write_text(cpp,encoding='utf-8')
for name in ['worker','launch']:
    s=(project_path(f'research_round8_clean_title_v3_{name}.py', base=R)).read_text(encoding='utf-8').replace('clean_title_v3','clean_title_v4').replace('research_round8_conditional_library.h','research_round8_clean_library.h').replace('research_round7_remaining_experts.cpp','research_round8_observer_separated.h')
    if name=='worker':
        oldcheck="old=json.loads((R/'clean_title_v2/a_128k.json').read_text());new=m['results'][0];assert [a['prediction_hash'] for a in old['arms']]==[a['prediction_hash'] for a in new['arms']], 'A replay changed unexpectedly';m['a_predictions_match_completed_v2']=True;save();"
        assert oldcheck in s;s=s.replace(oldcheck,'')
        s=s.replace("'repair':'v1 fixture-count repair preserved; v2 failed on a >4096-byte tag/comment. v3 keeps a bounded 129-byte tag prefix and 3-byte closing tail, and tracks quotes independently; adds a 6000-byte comment test. No probability-family or promotion threshold change.'", "'repair':'Scientific variant: collision-free syntax/run/source-surprise namespaces. Old namespaces overlap on 224 synthetic state keys; source-surprise is not intentionally included in constructor-run. All v1-v3 evidence retained. Same candidate family and promotion threshold.'")
    (project_path(f'research_round8_clean_title_v4_{name}.py', base=R)).write_text(s,encoding='utf-8')
out={'status':'PASS','old_kind1_kind2_shared_keys':len(before[1]&before[2]),'old_union_keys':len(set.union(*before)),'new_disjoint_keys':len(set.union(*after)),'example_old_collision':{'constructor':{'prev_class':2,'punct':0,'run':0,'content_rank_band':0},'surprise':{'prev_class':0,'punct':2,'surprise':0,'prev_rank_band':0},'key':1600},'scope':'Mathematical namespace audit of the existing observer; earlier likelihood scores remain causal and normalized, but feature attribution can be confounded.'}
(project_path('research_round8_context_namespace_audit.json', base=R)).write_text(json.dumps(out,indent=2));print(json.dumps(out))
