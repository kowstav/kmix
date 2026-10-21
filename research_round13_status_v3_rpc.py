from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,os,subprocess,time
W=Path('/kaggle/working/hp_round13');refs=[];out={'observed_at':time.time(),'jobs':[]}
for name in ('dispatch_v1.json','additional_dispatch_v1.json'):
    p=W/name
    if p.exists():
        value=json.loads(p.read_text());out[name]={'status':value['status'],'error':value.get('error'),'jobs':value['jobs']}
        refs.extend(r['verified_push']['actual_ref'] for r in value['jobs'] if r.get('verified_push'))
def check(ref):
    r=subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=25)
    message=r.stdout+r.stderr
    for key in ('KAGGLE_API_TOKEN','KAGGLE_KEY'):
        if os.environ.get(key):message=message.replace(os.environ[key],'[REDACTED]')
    return {'ref':ref,'exit':r.returncode,'status_output':message[-1500:]}
with ThreadPoolExecutor(max_workers=7) as pool:out['jobs']=list(pool.map(check,refs))
out['live_processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,psr,comm','--sort=-%cpu'],text=True).splitlines()[:12]
(W/'status_v3.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
