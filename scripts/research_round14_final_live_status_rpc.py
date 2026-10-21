from pathlib import Path
import json,subprocess
W=Path('/kaggle/working/hp_round14')
for name in ('guard_storage_parity_v1/manifest.json','guard_match_pipeline_v1.json'):
    p=W/name
    if p.exists():
        m=json.loads(p.read_text());print(name,json.dumps({k:v for k,v in m.items() if k not in ('cases','command')}),'cases',len(m.get('cases',[])))
print(subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,comm','--sort=-%cpu'],text=True).splitlines()[:9])
