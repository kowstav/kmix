from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,os,subprocess,time,traceback,zipfile
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_batch_outputs');R.mkdir(exist_ok=True)
M={'status':'CHECKING_COMMITTED_JOBS','started':time.time(),'pulls':[],'deletions':[]}
def save():(W/'batch_collection_v1.json').write_text(json.dumps(M,indent=2))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()
def pull(ref):
    d=R/ref.split('/')[1];assert not d.exists();d.mkdir()
    p=subprocess.run(['kaggle','kernels','output',ref,'-p',str(d)],capture_output=True,text=True,timeout=1500)
    return {'ref':ref,'exit':p.returncode,'message':(p.stdout+p.stderr)[-1500:],
      'files':[{'path':str(f.relative_to(d)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in d.rglob('*') if f.is_file()]}
try:
    assert not (W/'batch_collection_v1.json').exists();save()
    Path('/root/.config/kaggle').mkdir(parents=True,exist_ok=True)
    refs=[]
    for n in ('dispatch_v1.json','dispatch_v2.json'):
        m=json.loads((W/n).read_text());refs.extend(r['verified_push']['actual_ref'] for r in m['jobs'] if r.get('verified_push'))
    ready=[];M['statuses']=[]
    for ref in refs:
        p=subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=40)
        msg=p.stdout+p.stderr;M['statuses'].append({'ref':ref,'exit':p.returncode,'output':msg[-1200:]});save()
        if p.returncode==0 and ('KernelWorkerStatus.COMPLETE' in msg or 'KernelWorkerStatus.ERROR' in msg):ready.append(ref)
    with ThreadPoolExecutor(max_workers=5) as pool:
        for f in as_completed([pool.submit(pull,r) for r in ready]):M['pulls'].append(f.result());save()
    assert all(r['exit']==0 and r['files'] for r in M['pulls'])
    entries=[];zpath=W/'batch_compact_v1.zip'
    with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for p in sorted(R.rglob('*')):
            if p.is_file() and p.suffix in ('.json','.log','.cmx','.hpwg'):
                n=str(p.relative_to(R));z.write(p,n);entries.append({'path':n,'bytes':p.stat().st_size,'sha256':sha(p)})
        z.writestr('entries.json',json.dumps(entries,indent=2))
    M.update(status='COMPLETE_AVAILABLE_OUTPUTS_PRESERVED',finished=time.time(),compact={'path':str(zpath),'bytes':zpath.stat().st_size,'sha256':sha(zpath),'entries':len(entries)});save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
