from pathlib import Path
import json,subprocess,sys,zipfile,hashlib,time,traceback
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_native_dispatch');M={'status':'WAITING_FOR_NATIVE_PARITY','started':time.time(),'jobs':[],'deletions':[],'GPU':False,'paid_usd':0}
def save():(W/'native_dispatch_v3.json').write_text(json.dumps(M,indent=2))
try:
    assert not R.exists() and not (W/'native_dispatch_v3.json').exists();R.mkdir();save()
    deadline=time.time()+1200
    while True:
        m=json.loads((W/'native_cpu_preflight_v1/manifest.json').read_text())
        if m['status'].startswith('FAIL'):raise RuntimeError('native gate failed; no jobs submitted')
        if m['status']=='PASS_NEUTRAL_PARITY_AND_SIX_EXACT_INVERSES':break
        assert time.time()<deadline,'preflight wait deadline';time.sleep(20)
    M['status']='CREATING_PREVERIFIED_PRIVATE_BINARY_ASSET';save()
    p=subprocess.run(['python3','/kaggle/working/research_round14_native_asset_worker.py'],stdout=(W/'native_asset_worker.log').open('ab'),stderr=subprocess.STDOUT,timeout=1200)
    assert p.returncode==0 and json.loads((W/'native_cpu_asset_v1.json').read_text())['status']=='COMPLETE_PRIVATE_ASSET_CREATED'
    with zipfile.ZipFile(W/'kernels_native_v3.zip.dat') as z:
        for n in z.namelist():assert (R/n).resolve().is_relative_to(R)
        z.extractall(R)
    sys.path.insert(0,'/root/r14_native_cpu_preflight/code');from hutter_research.dispatch_contracts import parse_successful_push
    P=json.loads((W/'prepared_native_v3.json').read_text());M['status']='PUSHING_FOUR_PRIVATE_CPU_JOBS';save()
    for job in P['jobs']:
        folder=R/job['folder'];assert hashlib.sha256((folder/'main.py').read_bytes()).hexdigest()==job['main_sha256']
        meta=json.loads((folder/'kernel-metadata.json').read_text());assert meta['is_private'] and not meta['enable_gpu'] and not meta['enable_internet']
        q=subprocess.run(['kaggle','kernels','list','--mine','--search',job['ref'].split('/')[1],'--csv'],capture_output=True,text=True,timeout=45)
        assert q.returncode==0 and job['ref'] not in q.stdout,'already exists or lookup failed; inspect instead of duplicate'
        p=subprocess.run(['kaggle','kernels','push','-p',str(folder)],capture_output=True,text=True,timeout=180)
        row={**job,'exit':p.returncode,'verified_push':None}
        try:row['verified_push']=parse_successful_push(p.stdout,'chaoscpp') if p.returncode==0 else None
        except ValueError:pass
        if not row['verified_push']:row['error']=(p.stdout+p.stderr)[-1600:]
        M['jobs'].append(row);save();assert row['verified_push'],'unverified push or quota; stop, do not retry or bypass'
    M.update(status='COMPLETE_FOUR_VERIFIED_PRIVATE_CPU_PUSHES',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED_NO_RETRY',error=repr(e),traceback=traceback.format_exc());save();raise
