from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,os,subprocess,time
W=Path('/kaggle/working/hp_round13');ROOT=W/'pulls';ROOT.mkdir(exist_ok=True)
refs=('chaoscpp/hutter-r13-constructor-descendants-v1','chaoscpp/hutter-r13-weight-storage-v1')
def pull(ref):
    target=ROOT/ref.rsplit('/',1)[1];target.mkdir(exist_ok=False)
    r=subprocess.run(['kaggle','kernels','output',ref,'-p',str(target)],capture_output=True,text=True,timeout=150)
    message=r.stdout+r.stderr
    for key in ('KAGGLE_API_TOKEN','KAGGLE_KEY'):
        if os.environ.get(key):message=message.replace(os.environ[key],'[REDACTED]')
    return {'ref':ref,'exit':r.returncode,'message':message[-5000:],'path':str(target),
        'files':[{'path':str(p.relative_to(target)),'bytes':p.stat().st_size} for p in target.rglob('*') if p.is_file()]}
with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(pull,refs))
out={'observed_at':time.time(),'pulls':rows}
(W/'completed_pull_v1.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
