"""Sequential early-stream warm diagnostic; no corpus-wide inference or timing qualification.

The unchanged retained native observer runs once from canonical offset zero.
Sixteen later windows share its genuine classical/neural history. Cold windows
are never relabelled warm. Encoding and decoding are separate processes.
"""
import pathlib,json,os,time,hashlib,subprocess,traceback,sys
import numpy as np
W=pathlib.Path('/kaggle/working');D=W/'hp_round10/warm_atlas_v1';D.mkdir(parents=True,exist_ok=False)
S=pathlib.Path('/root/hp_round10/warm_atlas_v1');S.mkdir(parents=True,exist_ok=False)
N=18*524288;K=524288
B=W/'hp_round8/native_stage_trace_v1/tree/cmix';T=B.parent
WEIGHTS=W/'hp_round7/lex_audit/lex_h1_run11.tfwc2';STREAM=W/'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt'
DICT=T/'dictionary/english.dic';VOCAB=W/'hp_round7/preserved/data/vocab.bm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while c:=f.read(1<<20):h.update(c)
 return h.hexdigest()
m={'id':'R10-E0-early-warm-atlas','status':'PREPARING','pid':os.getpid(),'started':time.time(),'scratch':str(S),
 'protocol':{'bytes':N,'start':0,'warmup':2*K,'windows':16,'window_bytes':K,'window_offsets':[2*K+i*K for i in range(16)],
 'selection':'frozen before native trace observation','regime':'early-stream sequential warm; all before-target native state advanced from canonical offset zero',
 'limits':'single early region, not independent corpus strata; lab observer build without PGO/LTO; Kaggle timing is diagnostic; no full-file saving estimate accepted',
 'replay':'same native baseline warmth for every source; online candidate state must advance from zero through warmup',
 'GPU':False,'deletions':[]},'paid_usd':0,'accounting':{}}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def run(args,label,env):
 start=time.monotonic()
 with (D/(label+'.log')).open('x') as log:
  p=subprocess.Popen(args,cwd=S,env=env,stdout=log,stderr=subprocess.STDOUT)
  m['child_pid']=p.pid;save(label+' running')
  _,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 row={'wall_seconds':time.monotonic()-start,'CPU_user_seconds':u.ru_utime,'CPU_system_seconds':u.ru_stime,'peak_RSS_KiB':u.ru_maxrss,'exit_code':p.returncode}
 m['accounting'][label]=row;assert p.returncode==0,(label,row)
try:
 start_wait=time.time()
 while True:
  pf=W/'hp_round10/preflight_v3/manifest.json'
  if pf.exists():
   readiness=json.loads(pf.read_text())
   if readiness['status'].startswith('COMPLETE'):break
   if readiness['status']=='FAIL':raise RuntimeError(readiness['error'])
  assert time.time()-start_wait<700
  time.sleep(5)
 assert sha(B)=='17768b0673e5a1ad6fb39ca86af25d6d40db3b1790fc17e365341456819fd3fa'
 assert sha(WEIGHTS)=='948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71'
 assert sha(DICT)=='4c8568cca9343b9a6212477880f56f8efd162f8784224a25edd043097d36215a'
 inp=S/'input.bin'
 with STREAM.open('rb') as f:raw=f.read(N)
 assert len(raw)==N;inp.write_bytes(raw);(S/'.dict').symlink_to(DICT)
 m['input_sha256']=sha(inp);m['binary_sha256']=sha(B);m['canonical_source_bytes']=STREAM.stat().st_size
 base={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_PREPARE','HP_LEX_'))}
 base.update(LAB_RAW='1',LAB_VOCAB=str(VOCAB),LAB_DICT=str(DICT),LAB_KEEP_TEMP='1',OMP_NUM_THREADS='1')
 archive=S/'out.cmx';cost=S/'cost.f32';q=S/'final_p.u16';stage=S/'stage.f32';hidden=S/'hidden.q8'
 m['status']='RUNNING_SEQUENTIAL_NATIVE_ENCODE';save('matched warmth protocol frozen; encoder starting')
 run([str(B),'-n','--transformer',str(WEIGHTS),str(inp),str(archive)],'encode',
 {**base,'LAB_COST':str(cost),'LAB_BITTRACE':str(q),'LAB_STAGETRACE':str(stage),'LAB_HIDDENTRACE':str(hidden)})
 assert cost.stat().st_size==4*N and q.stat().st_size==16*N and stage.stat().st_size==12+608*N and hidden.stat().st_size==193*N
 values=np.memmap(cost,'<f4','r',shape=(N,));m['warm_windows']=[{'offset':o,'bytes':K,'baseline_bits':float(np.asarray(values[o:o+K],np.float64).sum()),'history_bytes':o} for o in m['protocol']['window_offsets']]
 m['archive_bytes']=archive.stat().st_size;m['archive_sha256']=sha(archive)
 m['trace_sha256']={p.name:sha(p) for p in [cost,q,stage,hidden]};m['status']='RUNNING_INDEPENDENT_NATIVE_DECODE';save('warm traces complete; separately decoding full prefix')
 run([str(B),'-d','--transformer',str(WEIGHTS),str(archive),'decoded.bin'],'decode',base)
 assert sha(S/'decoded.bin')==m['input_sha256'];m['independent_decode_exact']=True
 m.update(status='COMPLETE_SEQUENTIAL_EARLY_WARM_ATLAS_AND_INDEPENDENT_DECODE',finished=time.time())
 save('sixteen warm windows recorded with matched state; early diagnostic only')
except BaseException as e:
 m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
