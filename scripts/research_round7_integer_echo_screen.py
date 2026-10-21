"""I03b fixed causal echo comparison after I01b search repair; no neural SGD."""
import pathlib,json,hashlib,numpy as np
import research_round7_idea_arch_screen as M
from research_round7_wrt import load_dictionary
out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'idea_arch_integer_echo_v1';dest.mkdir(exist_ok=False)
metadata=json.loads((out/'idea_arch_integer_graph_v1/results.json').read_text())
assert metadata['CPU_GPU_all_scores_equal_on_queries']==133,'Integer graph control failed'
dictionary=load_dictionary(out/'preserved/gen/.dict');words=list(dictionary.values());N=len(words)
assert hashlib.sha256((out/'preserved/gen/.dict').read_bytes()).hexdigest()==metadata['dictionary_sha256']
M.tests();old_graphs,old_meta=M.graph(words)
packed=np.load(out/'idea_arch_integer_graph_v1/graph.npz');ids=packed['ids'];scores=packed['scores']
assert ids.shape==scores.shape==(N,8) and np.all(ids!=np.arange(N)[:,None])
assert np.all(np.diff(np.sort(ids.astype(np.int32),axis=1),axis=1)>0),'Duplicate neighbors'
integer=[];random=[]
for i,w in enumerate(words):
    z=sum(int(s) for s in scores[i]);weights=[int(s)/z for s in scores[i]] if z else [1/8]*8
    row=[(int(v),p) for v,p in zip(ids[i],weights)];integer.append(row);control=[];used={i}
    for v,weight in row:
        lo=v//256*256;hi=min(N,lo+256);pool=[j for j in range(lo,hi) if j not in used and abs(len(words[j])-len(words[v]))<=1]
        if not pool:pool=[j for j in range(N) if j not in used]
        d=int.from_bytes(hashlib.blake2s(w+v.to_bytes(4,'little')+b'control42',digest_size=4).digest(),'little')
        t=pool[d%len(pool)];used.add(t);control.append((t,weight))
    random.append(control)
assert all(abs(sum(p for _,p in row)-1)<1e-12 for row in integer+random)
graphs=[old_graphs[0],old_graphs[1],integer,random]
meta={**old_meta,'variant':'I03b only moment graph and its matched-random control replaced by exhaustive integer Q1024 graph',
      'integer_graph':metadata,'unchanged_prefix_suffix_and_deletion_channels':True,
      'graph_edges':sum(len(row) for g in graphs for row in g),
      'examples':{w:{name:[words[v].decode('ascii',errors='replace') for v,_ in graphs[c][words.index(w.encode())]] for c,name in enumerate(['prefix_suffix','deletion_signature','integer_letter_moment','matched_random'])} for w in ['no','know','now','diamond','the'] if w.encode() in words}}
M.GRAPH_CACHE[tuple(words)]=(graphs,meta);rows=[]
for n in 'abcd':
    p=out/'preserved/slices'/(n+'2m.bin') if n in 'ab' else out/(n+'2m.bin');cp=out/'lex_native_2m'/(n+'_cost.f32')
    raw=p.read_bytes();cost=np.fromfile(cp,'<f4');assert len(raw)==len(cost)==2000000
    r=M.screen(raw,cost,dictionary,diagnostic=False)
    r.update(input_sha256=hashlib.sha256(raw).hexdigest(),cost_sha256=hashlib.sha256(cp.read_bytes()).hexdigest(),
             source_sha256=hashlib.sha256((out/'research_round7_integer_echo_screen.py').read_bytes()).hexdigest(),
             core_scorer_sha256=hashlib.sha256((out/'research_round7_idea_arch_screen.py').read_bytes()).hexdigest())
    (dest/(n+'.json')).write_text(json.dumps(r,indent=2));rows.append({'slice':n,'saving_bytes':r['score']['prequential_saving_bytes'],'wall_seconds':r['wall_seconds']})
    (dest/'summary.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows[-1]),flush=True)
print('INTEGER_ECHO_SCREEN_COMPLETE',flush=True)
