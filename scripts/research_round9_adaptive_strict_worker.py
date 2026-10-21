"""Strict-FP standalone replay. Reuses the completed fresh G observation."""
import pathlib,json,time,os,hashlib,subprocess,traceback,ast,math,shutil
import numpy as np
from scipy.special import expit
from numba import njit
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'adaptive_strict_v1';D.mkdir(exist_ok=False)
S=pathlib.Path('/root/hp_round9/adaptive_strict_v1');S.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
try:
 for local,dest in [('research_round9_adaptive_law.h','hp_adaptive_law.h'),('research_round9_adaptive_law.cpp','hp_adaptive_law.cpp')]:
  (S/dest).write_bytes((R/local).read_bytes())
 # Keep the historical scratch aliases, while supporting the corrected include
 # used by the source as stored in the repository.
 (S/'research_round9_adaptive_law.h').write_bytes((R/'research_round9_adaptive_law.h').read_bytes())
 compiler='/kaggle/working/hp_round8/native_stage_trace_v1/compiler/usr/bin/clang++-17'
 # Reuse the restored compiler path and environment from the preceding build.
 old=json.loads((R/'adaptive_native_v1/manifest.json').read_text());assert old['status']=='FAIL'
 compiler=shutil.which('clang++-17');assert compiler
 subprocess.run([compiler,'-O3','-std=c++17','-march=x86-64-v3','-mrecip=none','-ffp-contract=off','-DHP_ADAPTIVE_REPLAY_MAIN','hp_adaptive_law.cpp','-o','replay'],cwd=S,check=True)
 nodes=ast.parse((R/'research_round9_adaptive_source_worker.py').read_text());fs=[n for n in nodes.body if isinstance(n,ast.FunctionDef) and n.name=='replay'];ns={'np':np,'math':math,'njit':njit};exec(compile(ast.Module(body=fs,type_ignores=[]),'<preserved-replay>','exec'),ns)
 T=pathlib.Path('/root/hp_round9/adaptive_native_v1/g_teacher');save('strict-FP C++ replay on reused G traces')
 start=time.monotonic();subprocess.run([str(S/'replay'),*[str(T/p) for p in ['input.bin','final_p.u16','hidden.q8','stage.f32']],str(S/'q.u16')],check=True);m['strict_CPP_seconds']=time.monotonic()-start
 p=np.fromfile(T/'final_p.u16','<u2');data=np.frombuffer((T/'input.bin').read_bytes(),'u1');ell=np.log(p.astype(np.float64)/(65536-p.astype(np.float64)));h=np.memmap(T/'hidden.q8','u1','r',shape=(len(data),193));valid=np.repeat(np.r_[0,h[:-1,0]],8);st=np.memmap(T/'stage.f32','<f4','r',offset=12,shape=(len(p),19));nn=np.clip(st[:,17].astype(np.float64),1/65536,65535/65536);feat=(np.clip(np.log(nn/(1-nn))-ell,-12,12)/12).astype(np.float32)*valid;dot=.0016181118716570748-.007454085408717222*ell+2.3818512619982752*feat;ex=np.column_stack([p,*[np.clip(np.floor(65536*expit(ell+a*dot)+.5),1,65535).astype('<u2') for a in [.5,1.,1.5,2.]]]);y=((data[:,None]>>(7-np.arange(8)))&1).reshape(-1);q=ns['replay'](ex,y,2.6441431586476938e-06)[0];cq=np.fromfile(S/'q.u16','<u2');ix=np.where(q!=cq)[0]
 m.update(status='COMPLETE_STRICT_CPP_REPLAY' if len(ix)==0 else 'FAIL_STRICT_CPP_REPLAY',count=len(q),unequal_Q16_events=len(ix),first_mismatches=[{'index':int(i),'reference':int(q[i]),'CPP':int(cq[i])} for i in ix[:12]],strict_Q16_sha256=sha(S/'q.u16'),reference_Q16_sha256=hashlib.sha256(q.tobytes()).hexdigest(),source_sha256=sha(S/'hp_adaptive_law.cpp'),finished=time.time());save('strict-FP replay compared; native core was not rerun')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
