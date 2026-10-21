from pathlib import Path
import hashlib,json,os,subprocess,sys,time,traceback,zipfile
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_dispatch_v1');M={'status':'PREFLIGHT','started':time.time(),'jobs':[],'deletions':[],'paid_usd':0,'GPU':False}
def save():(W/'dispatch_v1.json').write_text(json.dumps(M,indent=2))
try:
    assert not R.exists() and not (W/'dispatch_v1.json').exists();R.mkdir();save()
    with zipfile.ZipFile(W/'kernels_v1.zip.dat') as z:
        for name in z.namelist():assert (R/name).resolve().is_relative_to(R)
        z.extractall(R)
    P=json.loads((W/'prepared_v1.json').read_text());sys.path.insert(0,'/root/r14_code_v1')
    from hutter_research.dispatch_contracts import parse_successful_push
    for job in P['jobs']:
        folder=R/job['folder'];assert hashlib.sha256((folder/'main.py').read_bytes()).hexdigest()==job['main_sha256']
        meta=json.loads((folder/'kernel-metadata.json').read_text());assert meta['is_private'] and not meta['enable_gpu'] and not meta['enable_internet']
        check=subprocess.run(['kaggle','kernels','list','--mine','--search',job['ref'].split('/')[1],'--csv'],capture_output=True,text=True,timeout=40)
        assert check.returncode==0 and job['ref'] not in check.stdout,'already submitted or status unknown; do not duplicate'
        p=subprocess.run(['kaggle','kernels','push','-p',str(folder)],capture_output=True,text=True,timeout=240)
        result={**job,'exit':p.returncode}
        try:result['verified_push']=parse_successful_push(p.stdout,'chaoscpp') if p.returncode==0 else None
        except ValueError:result['verified_push']=None
        if not result['verified_push']:
            msg=p.stdout+p.stderr
            for k in ('KAGGLE_API_TOKEN','KAGGLE_KEY'):
                if os.environ.get(k):msg=msg.replace(os.environ[k],'[REDACTED]')
            result['failure']=msg[-2000:]
        M['jobs'].append(result);save();assert result['verified_push'],'unverified push; no automatic retry or quota bypass'
    M.update(status='COMPLETE_FOUR_VERIFIED_PUSHES',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED_NO_RETRY',error=repr(e),traceback=traceback.format_exc());save();raise
