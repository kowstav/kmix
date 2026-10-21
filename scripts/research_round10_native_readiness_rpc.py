import pathlib,json,shutil,hashlib,subprocess
W=pathlib.Path('/kaggle/working')
out={'tools':{n:shutil.which(n) for n in ['g++','clang++-17','make','kaggle']},'native':[],'Kaggle_cli_version':subprocess.run(['kaggle','--version'],capture_output=True,text=True).stdout.strip()}
for root in [W/'hp_round8/native_stage_trace_v1/tree',W/'hp_round7/preserved/bin',W/'hp_round8/native_stage_weak_confirmation_v1']:
 if root.exists():
  for p in root.rglob('*'):
   if p.is_file() and (p.name in ['cmix','english.dic','makefile'] or p.suffix=='.tfwc2'):
    out['native'].append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
print(json.dumps(out))
