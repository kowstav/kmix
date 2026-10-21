import pathlib,json,shutil
R=pathlib.Path('/kaggle/working/hp_round9');m={'free_working':shutil.disk_usage(R).free,'files':[]}
for p in R.rglob('*'):
 if p.is_file() and p.suffix in ['.pt','.bin','.zip']:m['files'].append({'file':str(p),'bytes':p.stat().st_size})
print(json.dumps(m))
