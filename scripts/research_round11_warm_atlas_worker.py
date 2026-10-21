"""Sequential native warm history, with a corrected serialized-vocabulary gate."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
import traceback
import numpy as np

W=Path('/kaggle/working')
D=W/'hp_round11/warm_atlas_v2'
D.mkdir(parents=True,exist_ok=False)
S=Path('/root/hp_round11/warm_atlas_v2')
S.mkdir(parents=True,exist_ok=False)
N=18*524288
K=524288
B=W/'hp_round8/native_stage_trace_v1/tree/cmix'
T=B.parent
WEIGHTS=W/'hp_round7/lex_audit/lex_h1_run11.tfwc2'
STREAM=W/'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt'
DICT=T/'dictionary/english.dic'
VOCAB=W/'hp_round7/preserved/data/vocab.bm'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while block:=f.read(1<<20):
            h.update(block)
    return h.hexdigest()

M={'id':'R11-sequential-early-warm-atlas','status':'PREPARING','pid':os.getpid(),'started':time.time(),
   'scratch':str(S),'paid_usd':0,'deletions':[],'accounting':{},
   'protocol':{'bytes':N,'start':0,'warmup':2*K,'windows':16,'window_bytes':K,
               'window_offsets':[2*K+i*K for i in range(16)],
               'regime':'one early-region cluster; native/candidate states must advance through every prior byte',
               'selection':'window positions frozen before new traces; no independent-corpus or full-package inference',
               'GPU':False}}

def save(stage):
    M['stage']=stage
    (D/'manifest.json').write_text(json.dumps(M,indent=2))
    print(stage,flush=True)

def run(args,label,env):
    started=time.monotonic()
    with (D/(label+'.log')).open('x') as log:
        process=subprocess.Popen(args,cwd=S,env=env,stdout=log,stderr=subprocess.STDOUT)
        M['child_pid']=process.pid
        save(label+' running')
        _,status,usage=os.wait4(process.pid,0)
    code=os.waitstatus_to_exitcode(status)
    M['accounting'][label]={'wall_seconds':time.monotonic()-started,'CPU_user_seconds':usage.ru_utime,
        'CPU_system_seconds':usage.ru_stime,'peak_RSS_KiB':usage.ru_maxrss,'exit_code':code}
    assert code==0,(label,code)

try:
    readiness=json.loads((W/'hp_round11/preflight_v4/manifest.json').read_text())
    assert readiness['status']=='COMPLETE_NATIVE_PREFLIGHT_PASS_SERIALIZED_VOCABULARY'
    for path,expected in [(B,'17768b0673e5a1ad6fb39ca86af25d6d40db3b1790fc17e365341456819fd3fa'),
        (WEIGHTS,'948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71'),
        (DICT,'4c8568cca9343b9a6212477880f56f8efd162f8784224a25edd043097d36215a')]:
        assert sha(path)==expected
    with STREAM.open('rb') as f:
        raw=f.read(N)
    assert len(raw)==N
    (S/'input.bin').write_bytes(raw)
    (S/'.dict').symlink_to(DICT)
    M['input_sha256']=sha(S/'input.bin')
    M['binary_sha256']=sha(B)
    M['canonical_source_bytes']=STREAM.stat().st_size
    base={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_PREPARE','HP_LEX_'))}
    base.update(LAB_RAW='1',LAB_VOCAB=str(VOCAB),LAB_DICT=str(DICT),LAB_KEEP_TEMP='1',OMP_NUM_THREADS='1')
    paths={name:S/name for name in ['out.cmx','cost.f32','final_p.u16','stage.f32','hidden.q8']}
    M['status']='RUNNING_SEQUENTIAL_NATIVE_ENCODE'
    run([str(B),'-n','--transformer',str(WEIGHTS),'input.bin','out.cmx'],'encode',
        {**base,'LAB_COST':str(paths['cost.f32']),'LAB_BITTRACE':str(paths['final_p.u16']),
         'LAB_STAGETRACE':str(paths['stage.f32']),'LAB_HIDDENTRACE':str(paths['hidden.q8'])})
    for name,size in [('cost.f32',4*N),('final_p.u16',16*N),('stage.f32',12+608*N),('hidden.q8',193*N)]:
        assert paths[name].stat().st_size==size,(name,paths[name].stat().st_size,size)
    costs=np.memmap(paths['cost.f32'],dtype='<f4',mode='r',shape=(N,))
    M['warm_windows']=[{'offset':o,'bytes':K,'baseline_bits':float(np.asarray(costs[o:o+K],np.float64).sum()),
                       'history_bytes':o} for o in M['protocol']['window_offsets']]
    M['archive_bytes']=paths['out.cmx'].stat().st_size
    M['archive_sha256']=sha(paths['out.cmx'])
    M['status']='RUNNING_INDEPENDENT_NATIVE_DECODE'
    run([str(B),'-d','--transformer',str(WEIGHTS),'out.cmx','decoded.bin'],'decode',base)
    assert sha(S/'decoded.bin')==M['input_sha256']
    M['independent_decode_exact']=True
    M['trace_sha256']={name:sha(path) for name,path in paths.items() if name!='out.cmx'}
    # Preserve the compact actual archive on carried working storage too.
    (D/'out.cmx').write_bytes(paths['out.cmx'].read_bytes())
    M.update(status='COMPLETE_SEQUENTIAL_EARLY_WARM_ATLAS_AND_INDEPENDENT_DECODE',finished=time.time())
    save('native archive exact; sixteen adjacent warm windows are one early dependence cluster')
except BaseException as error:
    M.update(status='FAIL',error=repr(error),traceback=traceback.format_exc(),finished=time.time())
    save('failure preserved')
    raise
