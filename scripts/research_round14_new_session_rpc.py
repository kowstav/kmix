from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,os,subprocess,shutil,time
W=Path('/kaggle/working/hp_round14');out={'observed_at':time.time(),'manifests':{}}
names=['dispatch_v1.json','dispatch_v2.json','full_serialized_verification_v1.json','word_costs/manifest.json','detail_preservation.json']
refs=[]
for n in names:
    p=W/n
    if not p.exists():continue
    m=json.loads(p.read_text());out['manifests'][n]={k:v for k,v in m.items() if k not in ('cases','shards','groups')}
    out['manifests'][n]['cases_or_shards']=len(m.get('cases',m.get('shards',[])))
    refs.extend(r['verified_push']['actual_ref'] for r in m.get('jobs',[]) if r.get('verified_push'))
def check(ref):
    p=subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=30)
    return {'ref':ref,'exit':p.returncode,'output':(p.stdout+p.stderr)[-1200:]}
with ThreadPoolExecutor(max_workers=5) as pool:out['jobs']=list(pool.map(check,refs))
out['disk']={p:dict(zip(('total','used','free'),shutil.disk_usage(p))) for p in ('/root','/kaggle/working')}
out['processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,psr,comm','--sort=-%cpu'],text=True).splitlines()[:12]
out['root_preserved']={p:Path(p).exists() for p in ('/root/hp_round14_pulls','/root/r14_code_v2','/root/r14_dispatch_v2')}
print(json.dumps(out))
