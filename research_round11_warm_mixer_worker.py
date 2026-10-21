"""Reuse the 9 MiB sequential native trajectory; never launch another observer."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import json
import os
import subprocess
import time
import traceback
import numpy as np

W=Path('/kaggle/working/hp_round11/warm_mixer_v1')
S=Path('/root/hp_round11_warm_mixer_v1')
assert not W.exists() and not S.exists(), 'Inspect this registered longer episode rather than duplicate'
W.mkdir(parents=True); S.mkdir()
T=Path('/root/hp_round11/warm_atlas_v2')
A=Path('/kaggle/working/hp_round11/warm_atlas_v2/manifest.json')
CODE=Path('/root/hp_round11_private_assets_v2/code/hutter_research')
N=9437184; K=524288
ARMS=[('identity',1000),('full',250),('full',1000),('full',4000),('global',1000),
      ('no_explicit_nn',1000),('relabel',1000),('long_memory',250),('long_memory',1000),
      ('long_memory',4000),('short_memory',1000),('memory_zero',1000)]
M={'status':'WAITING_FOR_EXISTING_WARM_NATIVE_TRACE','pid':os.getpid(),'started':time.time(),
   'deletions':[],'paid_usd':0,'GPU':False,'replays':[],'arms':ARMS,
   'production_package_qualified':False,'native_observer_launches':0,
   'protocol':{'start':0,'bytes':N,'warmup_bytes':2*K,'memory_horizons':[1,1024,32768,131072],
      'development_windows':[2*K+i*K for i in range(6)],'confirmation_windows':[8*K+i*K for i in range(10)],
      'selection_candidates':['full_250','full_1000','full_4000','long_memory_250','long_memory_1000','long_memory_4000'],
      'regime':'one early dependence cluster; state advances through every prior byte',
      'qualification':'unchanged-native-trajectory replay only; actual candidate archives and deployment code/resources still required'}}

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(1<<20): h.update(b)
    return h.hexdigest()
def save(): (W/'manifest.json').write_text(json.dumps(M,indent=2))

def replay(arm,rate):
    label=f'{arm}_{rate}'; path=S/(label+'.u16')
    started=time.monotonic()
    command=[str(S/'integer_replay'),str(T/'input.bin'),str(T/'final_p.u16'),str(T/'hidden.q8'),str(T/'stage.f32'),str(path),arm,str(rate)]
    result=subprocess.run(command,capture_output=True,text=True)
    assert result.returncode==0,(label,result.returncode,result.stderr[-500:])
    stats=json.loads(result.stdout); assert stats['bytes']==N
    assert path.stat().st_size==16*N
    reference=np.memmap(T/'final_p.u16',dtype='<u2',mode='r',shape=(N,8))
    candidate=np.memmap(path,dtype='<u2',mode='r',shape=(N,8))
    data=np.memmap(T/'input.bin',dtype='u1',mode='r',shape=(N,))
    windows=[]; full_gain=0.
    for o in range(0,N,K):
        bits=((np.asarray(data[o:o+K])[:,None]>>(7-np.arange(8)))&1).astype(bool)
        p=np.asarray(reference[o:o+K],dtype=np.uint32); q=np.asarray(candidate[o:o+K],dtype=np.uint32)
        assert (q>0).all() and (q<65536).all()
        lp=np.where(bits,p,65536-p); lq=np.where(bits,q,65536-q)
        gain=float(np.log2(lq.astype(np.float64)/lp).sum())/8; full_gain+=gain
        if o>=2*K: windows.append({'offset':o,'bytes':K,'gain_byte_equivalent':gain})
    assert abs(full_gain-stats['gain_byte_equivalent'])<0.0001
    digest=sha(path)
    if arm=='identity': assert digest==sha(T/'final_p.u16')
    return {'arm':arm,'rate':rate,'label':label,'Q16_sha256':digest,'all_probabilities_supported':True,
            'windows':windows,'whole_prefix_gain_byte_equivalent':full_gain,
            'development_gain_byte_equivalent':sum(r['gain_byte_equivalent'] for r in windows if r['offset']<8*K),
            'confirmation_gain_byte_equivalent':sum(r['gain_byte_equivalent'] for r in windows if r['offset']>=8*K),
            'replay_wall_seconds':time.monotonic()-started,'diagnostic':stats}

try:
    save()
    for name in ['integer_mixer.h','long_memory.h','integer_mixer_replay.cpp','probability_tables.inc','probability_tables.bin']:
        M.setdefault('source_files',{})[name]={'bytes':(CODE/name).stat().st_size,'sha256':sha(CODE/name)}
    compiled=subprocess.run(['g++','-O2','-std=c++17','-fno-fast-math','-ffp-contract=off',str(CODE/'integer_mixer_replay.cpp'),'-o',str(S/'integer_replay')],capture_output=True,text=True)
    assert compiled.returncode==0,compiled.stderr[-1000:]
    while True:
        atlas=json.loads(A.read_text())
        if atlas['status']=='FAIL': raise RuntimeError('Native atlas failed')
        if atlas['status'] in ['RUNNING_INDEPENDENT_NATIVE_DECODE','COMPLETE_SEQUENTIAL_EARLY_WARM_ATLAS_AND_INDEPENDENT_DECODE']: break
        time.sleep(45)
    for name,size in [('input.bin',N),('final_p.u16',16*N),('hidden.q8',193*N),('stage.f32',608*N+12)]:
        assert (T/name).stat().st_size==size
    M.update(status='RUNNING_TWELVE_WARM_REPLAY_ARMS',native_input_sha256=sha(T/'input.bin'),native_Q16_sha256=sha(T/'final_p.u16'))
    save()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(replay,arm,rate) for arm,rate in ARMS]
        for future in as_completed(futures): M['replays'].append(future.result()); save()
    labels={r['label']:r for r in M['replays']}
    assert labels['full_1000']['Q16_sha256']==labels['relabel_1000']['Q16_sha256']
    selected=max((labels[name] for name in M['protocol']['selection_candidates']),key=lambda r:r['development_gain_byte_equivalent'])
    M.update(status='COMPLETE_WARM_REPLAY_NATIVE_DECODE_PENDING',selected_by_development_only=selected['label'],
             selected_confirmation_gain_byte_equivalent=selected['confirmation_gain_byte_equivalent'],finished=time.time(),
             ablation_controls_Q16_identity_PASS=True)
    save()
    while True:
        atlas=json.loads(A.read_text())
        if atlas['status']=='FAIL': raise RuntimeError('Native independent decode failed')
        if atlas['status']=='COMPLETE_SEQUENTIAL_EARLY_WARM_ATLAS_AND_INDEPENDENT_DECODE':
            assert atlas['independent_decode_exact']
            M.update(status='COMPLETE_TWELVE_SEQUENTIAL_WARM_REPLAYS_ONLY',baseline_independent_decode_exact=True,
                     native_atlas_manifest_sha256=sha(A),qualification_finished=time.time()); save(); break
        time.sleep(45)
except BaseException as error:
    M.update(status='FAIL',error=repr(error),traceback=traceback.format_exc(),finished=time.time()); save(); raise
