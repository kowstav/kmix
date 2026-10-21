"""Submit the five frozen private four-worker jobs once; verify API success."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,time,traceback,zipfile

W=Path('/kaggle/working/hp_round13');OUT=W/'dispatch_v1.json'
M={'status':'VERIFYING_PRECONDITIONS','started':time.time(),'pid':os.getpid(),'jobs':[],
   'deletions':[],'paid_usd':0,'GPU':False}
def save():OUT.write_text(json.dumps(M,indent=2))
def call(args,timeout=180):
    p=subprocess.run(['kaggle',*args],capture_output=True,text=True,timeout=timeout)
    return p.returncode,p.stdout,p.stderr
try:
    assert not OUT.exists(),'read existing dispatch; do not relaunch'
    assert json.loads((W/'preflight_v1.json').read_text())['status']=='PASS_LINUX_SOURCE_AND_STREAM_PREFLIGHT'
    asset=json.loads((W/'asset_prepare_manifest.json').read_text())
    assert asset['status']=='COMPLETE_PRIVATE_CPU_ASSETS_CREATED',asset['status']
    S=Path('/root/hp_round13_kernel_batch_v1');assert not S.exists();S.mkdir()
    with zipfile.ZipFile(W/'kernels_v1.zip') as z:
        for name in z.namelist():
            p=(S/name).resolve();assert p.is_relative_to(S.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
    sys.path.insert(0,'/root/hp_round13_preflight')
    from hutter_research.dispatch_contracts import parse_successful_push
    save();ready=False
    for delay in (0,10,20,30,60,60):
        if delay:time.sleep(delay)
        code,text,error=call(['datasets','status',asset['dataset']],timeout=30)
        assert code==0,'dataset status rejected; no automatic retry'
        if re.search(r'\b(ready|complete)\b',text,re.I):ready=True;break
    assert ready,'dataset not ready during bounded backoff; preserve state'
    M['status']='SUBMITTING_PRIVATE_FOUR_WORKER_JOBS';save()
    for job in ('warm-development','warm-confirmation','constructor-descendants','weight-storage','full-corpus-factorization'):
        folder=S/job;meta=json.loads((folder/'kernel-metadata.json').read_text());ref=meta['id']
        assert meta['is_private'] and not meta['enable_gpu'] and not meta['enable_tpu'] and not meta['enable_internet']
        assert meta['dataset_sources']==[asset['dataset']]
        code,listing,_=call(['kernels','list','--mine','--search',ref.split('/')[1],'--csv'],timeout=30)
        assert code==0,'owner inventory unavailable; stop before writes'
        assert ref not in listing,'existing reference: inspect source and reuse, do not overwrite'
        code,stdout,stderr=call(['kernels','push','-p',str(folder)],timeout=240)
        row={'requested_ref':ref,'CLI_exit':code,'worker_count':4,'source_sha256':hashlib.sha256((folder/'main.py').read_bytes()).hexdigest()}
        try:row['verified_push']=parse_successful_push(stdout,'chaoscpp') if code==0 else None
        except ValueError:row['verified_push']=None
        M['jobs'].append(row);save()
        assert row['verified_push'],'notebook API rejection or unverified result; no quota bypass or automatic retry'
    M.update(status='COMPLETE_FIVE_VERIFIED_PRIVATE_PUSHES',finished=time.time());save()
except BaseException as e:
    M.update(status='BLOCKED_OR_FAILED_NO_AUTOMATIC_RETRY',error=repr(e),traceback=traceback.format_exc(),finished=time.time());save();raise
