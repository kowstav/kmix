from pathlib import Path
import json,subprocess
W=Path('/kaggle/working/hp_round14');p=W/'native_cpu_preflight_v1/manifest.json';m=json.loads(p.read_text())
print(json.dumps({k:v for k,v in m.items() if k!='cases'}));print('cases',json.dumps([{'mode':r['mode'],'status':r['status'],'bytes':r.get('archive_bytes')} for r in m['cases']]))
print('processes',subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,comm','--sort=-%cpu'],text=True).splitlines()[:10])
