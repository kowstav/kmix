from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json,os,subprocess,shutil,time
W=Path('/kaggle/working/hp_round14');out={'observed_at':time.time(),'pyppmd_installed':bool(importlib.util.find_spec('pyppmd'))}
for name in ('dispatch_v1.json','dispatch_v2.json','full_serialized_verification_v1.json','preflight_v2.json'):
    p=W/name
    if p.exists():
        m=json.loads(p.read_text());out[name]={k:v for k,v in m.items() if k not in ('cases','traceback')};out[name]['completed_cases']=len(m.get('cases',[]))
out['processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,psr,comm','--sort=-%cpu'],text=True).splitlines()[:14]
out['disk_free']=shutil.disk_usage('/kaggle/working').free
print(json.dumps(out))
