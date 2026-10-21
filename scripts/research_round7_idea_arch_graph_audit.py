"""I01 bounded-search fidelity and independent letter basis audit; no fitting."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import pathlib,json,time,hashlib,resource,numpy as np
from research_round7_wrt import load_dictionary
from research_round7_idea_arch_screen import graph
out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'idea_arch_graph_audit_v1';dest.mkdir(exist_ok=False)
started=time.monotonic();words=list(load_dictionary(out/'preserved/gen/.dict').values());N=len(words);graphs,meta=graph(words)
f=np.zeros((N,3,26),np.float32)
for i,w in enumerate(words):
    for j,c in enumerate(w):
        if 97<=c<=122:
            u=(j+1)/len(w);f[i,:,c-97]+=[1,u,u*u]
counts=f[:,0].copy();f/=np.maximum(np.linalg.norm(f,axis=2,keepdims=True),1e-20)
index={w:i for i,w in enumerate(words)}
# Predeclared deterministic rank-spread queries plus the user proposal's examples.
queries=sorted(set(np.linspace(0,N-1,128,dtype=np.int64).tolist()+[index[w] for w in [b'no',b'know',b'now',b'diamond',b'the'] if w in index]))
rows=[];ranks={}
for qi,i in enumerate(queries):
    # Same three-channel cosine score as I03, but exhaustive over every leaf.
    scores=np.sum(np.sum(f*f[i],axis=2)*[.5,.3,.2],axis=1)
    scores[i]=-np.inf;order=np.lexsort((np.arange(N),-scores));top=order[:8].tolist();bounded=[v for v,_ in graphs[2][i]]
    row={'source_id':int(i),'word':words[i].decode('ascii',errors='replace'),'exhaustive_top8':[words[v].decode('ascii',errors='replace') for v in top],
         'bounded_top8':[words[v].decode('ascii',errors='replace') for v in bounded],
         'recall_at8':len(set(top)&set(bounded))/8,'mean_exact_top8_score':float(scores[top].mean()),
         'mean_bounded_top8_score':float(scores[bounded].mean()) if bounded else None}
    if words[i] in [b'no',b'know',b'now',b'diamond',b'the']:
        rank=np.empty(N,np.int32);rank[order]=np.arange(1,N+1)
        row['named_target_ranks']={w.decode():{'exhaustive_rank':int(rank[index[w]]),'score':float(scores[index[w]]),'bounded_hit':index[w] in bounded} for w in [b'no',b'know',b'now',b'diamond'] if w in index and index[w]!=i}
        ranks[row['word']]=row
    rows.append(row)
# Float32-byte-identical normalized-feature collisions are reported as such;
# absence of these would not prove injectivity over arbitrary words.
keys={};collision_groups=[]
for i,row in enumerate(f):keys.setdefault(row.tobytes(),[]).append(i)
for group in keys.values():
    if len(group)>1:collision_groups.append([words[i].decode('ascii',errors='replace') for i in group])
u=np.linspace(0,1,31,dtype=np.float64);basis=np.stack([np.ones_like(u),u,u*u]);five=np.vstack([basis,1-u,(1-u)**2])
assert np.linalg.matrix_rank(five)==3
assert np.allclose(five[3],basis[0]-basis[1]) and np.allclose(five[4],basis[0]-2*basis[1]+basis[2])
result={'scope':'Dictionary-only search/basis audit; not a corpus-fitted graph or compression gain',
        'dictionary_words':N,'queries':len(queries),'mean_recall_at8':float(np.mean([r['recall_at8'] for r in rows])),
        'zero_recall_queries':sum(r['recall_at8']==0 for r in rows),'full_recall_queries':sum(r['recall_at8']==1 for r in rows),
        'mean_score_regret':float(np.mean([r['mean_exact_top8_score']-r['mean_bounded_top8_score'] for r in rows if r['mean_bounded_top8_score'] is not None])),
        'normalized_float32_identical_feature_collision_groups':len(collision_groups),'collision_examples':collision_groups[:24],
        'five_moment_basis_rank':int(np.linalg.matrix_rank(five)),'graph':meta,'named_examples':ranks,
        'query_results':rows,'startup_and_audit_seconds':time.monotonic()-started,'prototype_peak_rss_kbytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'neural_training':False,'deletions':[],'paid_rental_usd':0,
        'source_sha256':hashlib.sha256((out/'research_round7_idea_arch_graph_audit.py').read_bytes()).hexdigest()}
(dest/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['query_results','graph','named_examples']},indent=2));print('GRAPH_AUDIT_COMPLETE',flush=True)
