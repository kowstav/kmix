import pathlib,json,shutil,os
roots=[pathlib.Path('/root/hp'),pathlib.Path('/kaggle/working/hp_round7'),pathlib.Path('/kaggle/working/hp_round8')]
result={'disks':{p:shutil.disk_usage(p)._asdict() for p in ['/tmp','/root','/kaggle/working']},'files':[]}
for root in roots:
 if root.exists():
  for p in root.rglob('*'):
   if p.is_file() and (p.suffix in ['.tch','.tfwc2','.py','.u8','.i32','.f16'] or p.name in ['weights_io.cpp','quantize.h','model_opt.cpp','manifest.json']):
    result['files'].append({'path':str(p),'bytes':p.stat().st_size})
print(json.dumps(result))
