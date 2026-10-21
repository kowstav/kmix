import json, os, shutil, subprocess
from pathlib import Path
out={'cwd':os.getcwd(),'directories':{},'disk':{},'processes':[]}
for s in ['/kaggle/working','/root','/root/hp','/root/hp_round7','/kaggle/working/hp_round7','/kaggle/input']:
 p=Path(s)
 if p.is_dir():out['directories'][s]=[{'name':q.name,'dir':q.is_dir(),'bytes':q.stat().st_size if q.is_file() else None} for q in sorted(p.iterdir())][:100]
 else:out['directories'][s]=None
for s in ['/','/kaggle/working']:
 u=shutil.disk_usage(s);out['disk'][s]={'total':u.total,'used':u.used,'free':u.free}
try:
 r=subprocess.run(['ps','-eo','pid,etimes,comm,args'],capture_output=True,text=True,timeout=5)
 out['processes']=[x[:350] for x in r.stdout.splitlines() if any(k in x for k in ['round7','round8','cmix','g++','clang']) and 'jupyter' not in x]
except Exception as e:out['process_error']=type(e).__name__
try:out['gpu']=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,timeout=5).stdout
except Exception as e:out['gpu_error']=type(e).__name__
print(json.dumps(out))
