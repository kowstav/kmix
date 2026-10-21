"""I01c CPU-only, one-core reconstruction of the saved exhaustive integer graph."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
cpu_affinity=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu_affinity[0]})
import pathlib,json,time,math,hashlib,resource,numpy as np
from research_round7_wrt import load_dictionary
out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'idea_arch_integer_graph_cpu_v1';dest.mkdir(exist_ok=False)
started=time.monotonic();u0=resource.getrusage(resource.RUSAGE_SELF)
words=list(load_dictionary(out/'preserved/gen/.dict').values());N=len(words);Q=1024;K=8
f=np.zeros((N,3,26),np.int32)
for i,w in enumerate(words):
    sums=[[0]*26 for _ in range(3)]
    for j,c in enumerate(w):
        if 97<=c<=122:
            for k,power in enumerate([1,j+1,(j+1)**2]):sums[k][c-97]+=power
    for k,row in enumerate(sums):
        norm2=sum(v*v for v in row)
        if norm2:f[i,k]=[math.isqrt((Q*v)**2//norm2) for v in row]
assert np.max(np.sum(f.astype(np.int64)**2,axis=2))<=Q*Q
a=f.reshape(N,78).astype(np.float32);b=(f*np.asarray([5,3,2],np.int32)[None,:,None]).reshape(N,78).astype(np.float32)
expected=np.load(out/'idea_arch_integer_graph_v1/graph.npz');ids=np.empty((N,K),np.uint16);scores=np.empty((N,K),np.uint32)
target_ids=np.arange(N,dtype=np.int64);feature_seconds=time.monotonic()-started;score_started=time.monotonic()
for lo in range(0,N,256):
    hi=min(N,lo+256);s=a[lo:hi]@b.T
    assert s.max()<=10*Q*Q and np.array_equal(s,s.round()),'CPU exact-score contract failed'
    key=s.astype(np.int64)*(N+1)+(N-target_ids)[None,:];key[np.arange(hi-lo),np.arange(lo,hi)]=-1
    take=np.argpartition(key,N-K,axis=1)[:,-K:];keys=np.take_along_axis(key,take,axis=1)
    order=np.argsort(-keys,axis=1);take=np.take_along_axis(take,order,axis=1)
    ids[lo:hi]=take.astype(np.uint16);scores[lo:hi]=np.take_along_axis(s,take,axis=1).astype(np.uint32)
    del key,s,take,keys,order
assert np.array_equal(ids,expected['ids']) and np.array_equal(scores,expected['scores']),'CPU reconstruction differs from GPU graph'
usage=resource.getrusage(resource.RUSAGE_SELF)
r={'scope':'CPU-only Python/NumPy construction prototype under concurrent research load, not a packaged/native prize-machine measurement',
   'dictionary_words':N,'Q':Q,'K':K,'exact_ID_and_score_cells_each':int(ids.size),'all_CPU_GPU_neighbors_and_scores_equal':True,
   'allowed_CPU_affinity_before':cpu_affinity,'actual_CPU_affinity':sorted(os.sched_getaffinity(0)),
   'BLAS_OMP_MKL_threads':1,'feature_construction_seconds':feature_seconds,'exhaustive_scoring_and_topK_seconds':time.monotonic()-score_started,
   'wall_seconds':time.monotonic()-started,'user_seconds':usage.ru_utime-u0.ru_utime,'system_seconds':usage.ru_stime-u0.ru_stime,
   'prototype_peak_rss_kbytes':usage.ru_maxrss,'graph_ID_sha256':hashlib.sha256(ids.tobytes()).hexdigest(),
   'numpy_version':np.__version__,'neural_training':False,'paid_rental_usd':0,'deletions':[],
   'source_sha256':hashlib.sha256((out/'research_round7_integer_graph_cpu_check.py').read_bytes()).hexdigest()}
(dest/'results.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));print('INTEGER_GRAPH_CPU_CHECK_COMPLETE',flush=True)
