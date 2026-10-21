import os,pathlib,json,shutil,subprocess,importlib.util
W=pathlib.Path('/kaggle/working')
out={'CPU_count':os.cpu_count(),'CPU_affinity':sorted(os.sched_getaffinity(0)),
 'GPU_available':bool(shutil.which('nvidia-smi')),'disks':{p:shutil.disk_usage(p)._asdict() for p in ['/root','/kaggle/working']},
 'roots':{},'processes':subprocess.check_output(['ps','-eo','pid,ppid,etime,pcpu,pmem,comm'],text=True),
 'CLI':shutil.which('kaggle'),'kaggle_package':bool(importlib.util.find_spec('kaggle')),
 'credential_presence':{k:bool(os.environ.get(k)) for k in ['KAGGLE_USERNAME','KAGGLE_KEY','KAGGLE_API_TOKEN']},
 'credential_file_present':(pathlib.Path.home()/'.kaggle/kaggle.json').is_file(),
 'memory':pathlib.Path('/proc/meminfo').read_text().splitlines()[:3]}
for root in [W,pathlib.Path('/kaggle/input'),pathlib.Path('/root/hp_round9')]:
 out['roots'][str(root)]=[{'name':p.name,'directory':p.is_dir(),'bytes':p.stat().st_size if p.is_file() else None} for p in root.iterdir()] if root.exists() else None
if (W/'hp_round9').exists():
 out['round9_manifests']={}
 for p in (W/'hp_round9').glob('*/manifest.json'):
  try:
   j=json.loads(p.read_text());out['round9_manifests'][p.parent.name]={k:j.get(k) for k in ['status','pid','stage','scratch','error']}
  except (OSError,json.JSONDecodeError):pass
print(json.dumps(out))
