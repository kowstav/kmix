from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, os, shutil, subprocess, time
W=Path('/kaggle/working'); out={'observed_at':time.time(),'manifests':{},'jobs':[]}
refs=set()
for name in ('dispatch_v1.json','additional_dispatch_v1.json','native_delivery_repair_v2.json'):
    p=W/'hp_round13'/name
    if p.exists():
        v=json.loads(p.read_text());out['manifests'][name]=v
        for row in v.get('jobs',[]):
            if row.get('verified_push'):refs.add(row['verified_push']['actual_ref'])
        def visit(x):
            if isinstance(x,dict):
                for k,v in x.items():
                    if k=='actual_ref' and isinstance(v,str) and '/' in v:refs.add(v)
                    visit(v)
            elif isinstance(x,list):
                for v in x:visit(v)
        visit(v)
refs.add('chaoscpp/hutter-r13-native-final-head-v2')
out['credentials_present']={k:bool(os.environ.get(k)) for k in ('KAGGLE_API_TOKEN','KAGGLE_USERNAME','KAGGLE_KEY')}
out['cli']=shutil.which('kaggle')
def check(ref):
    try:
        p=subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=25)
        s=p.stdout+p.stderr
        for k in ('KAGGLE_API_TOKEN','KAGGLE_KEY'):
            if os.environ.get(k):s=s.replace(os.environ[k],'[REDACTED]')
        return {'ref':ref,'exit':p.returncode,'output':s[-2500:]}
    except Exception as e:return {'ref':ref,'error':type(e).__name__}
if out['cli']:
    with ThreadPoolExecutor(max_workers=8) as pool:out['jobs']=list(pool.map(check,sorted(refs)))
out['disk']={p:dict(zip(('total','used','free'),shutil.disk_usage(p))) for p in ('/root','/kaggle/working')}
out['cpus']=sorted(os.sched_getaffinity(0))
out['processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,psr,comm','--sort=-%cpu'],text=True).splitlines()[:18]
out['top_level']=[{'name':p.name,'dir':p.is_dir()} for p in W.iterdir()]
out['recent_manifests']=[{'path':str(p.relative_to(W)),'size':p.stat().st_size} for p in W.glob('**/*manifest*.json')][-100:]
(W/'research_round14_inventory.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
