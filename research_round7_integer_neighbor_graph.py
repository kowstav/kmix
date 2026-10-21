"""I01b exhaustive dictionary neighbors with exactly representable FP32 scores.

Research GPU construction only. Packed graph/CPU reconstruction costs are not
free. There is no neural fitting, future corpus information or deletion.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import pathlib,json,time,hashlib,math,resource,numpy as np,torch
from research_round7_wrt import load_dictionary
out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'idea_arch_integer_graph_v1';dest.mkdir(exist_ok=False)
started=time.monotonic();dictionary=out/'preserved/gen/.dict';words=list(load_dictionary(dictionary).values());N=len(words);Q=1024;K=8
torch.set_num_threads(1);torch.backends.cuda.matmul.allow_tf32=False;torch.set_float32_matmul_precision('highest')
features=np.zeros((N,3,26),np.int32)
for i,w in enumerate(words):
    sums=np.zeros((3,26),np.int64)
    for j,c in enumerate(w):
        if 97<=c<=122:sums[:,c-97]+=[1,j+1,(j+1)**2]
    for k in range(3):
        norm2=sum(int(v)**2 for v in sums[k])
        if norm2:
            for c in range(26):features[i,k,c]=math.isqrt((Q*int(sums[k,c]))**2//norm2)
assert int(np.max(np.sum(features.astype(np.int64)**2,axis=2)))<=Q*Q
left=features.reshape(N,78).astype(np.float32)
right=(features*np.asarray([5,3,2],np.int32)[None,:,None]).reshape(N,78).astype(np.float32)
a=torch.from_numpy(left).cuda();b=torch.from_numpy(right).cuda();ids=np.empty((N,K),np.uint16);scores=np.empty((N,K),np.uint32)
torch.cuda.reset_peak_memory_stats();device_ids=torch.arange(N,device='cuda',dtype=torch.int64)
with torch.inference_mode():
    for lo in range(0,N,256):
        hi=min(N,lo+256);s=a[lo:hi]@b.T
        assert float(s.max())<=10*Q*Q and torch.equal(s,s.round()),'FP32 integer score contract failed'
        key=s.to(torch.int64)*(N+1)+(N-device_ids)[None,:]
        key[torch.arange(hi-lo,device='cuda'),torch.arange(lo,hi,device='cuda')]=-1
        ix=torch.topk(key,K,dim=1,largest=True,sorted=True).indices
        ids[lo:hi]=ix.cpu().numpy().astype(np.uint16);scores[lo:hi]=s.gather(1,ix).cpu().numpy().astype(np.uint32)
        del key,s,ix
torch.cuda.synchronize()
audit=json.loads((out/'idea_arch_graph_audit_v1/results.json').read_text());queries=[r['source_id'] for r in audit['query_results']]
cpu_started=time.monotonic();cpu=left[queries]@right.T
gpu=(a[queries]@b.T).cpu().numpy();assert np.array_equal(cpu,gpu),'CPU/GPU integer score parity failed'
cpu_seconds=time.monotonic()-cpu_started
index={w.decode('ascii',errors='replace'):i for i,w in enumerate(words)};recall=[];examples={}
for r in audit['query_results']:
    i=r['source_id'];expected={index[w] for w in r['exhaustive_top8']};got=set(ids[i].tolist());recall.append(len(expected&got)/K)
for w in ['no','know','now','diamond','the']:
    if w in index:examples[w]=[words[v].decode('ascii',errors='replace') for v in ids[index[w]]]
np.savez(dest/'graph.npz',ids=ids,scores=scores)
result={'scope':'Exact integer-defined exhaustive dictionary graph, research construction; not achieved compression or qualifying CPU startup',
        'dictionary_words':N,'dictionary_sha256':hashlib.sha256(dictionary.read_bytes()).hexdigest(),'Q':Q,'K':K,'blocks':256,
        'integer_score_upper_bound':10*Q*Q,'FP32_exact_integer_bound':2**24,'CPU_GPU_all_scores_equal_on_queries':len(queries),
        'CPU_subset_score_seconds':cpu_seconds,'mean_recall_at8_vs_original_float_score':float(np.mean(recall)),
        'full_recall_queries_vs_float_score':sum(r==1 for r in recall),'examples':examples,
        'raw_ID_bytes_per_copy':ids.nbytes,'raw_score_bytes_per_copy':scores.nbytes,
        'stored_graph_npz_bytes':(dest/'graph.npz').stat().st_size,'scores_can_be_reconstructed_from_dictionary':True,
        'neural_training':False,'paid_rental_usd':0,'deletions':[],
        'wall_seconds':time.monotonic()-started,'prototype_peak_rss_kbytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'gpu_peak_allocated_bytes':torch.cuda.max_memory_allocated(),
        'source_sha256':hashlib.sha256((out/'research_round7_integer_neighbor_graph.py').read_bytes()).hexdigest(),
        'graph_sha256':hashlib.sha256((dest/'graph.npz').read_bytes()).hexdigest()}
(dest/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True);print('INTEGER_NEIGHBOR_GRAPH_COMPLETE',flush=True)
