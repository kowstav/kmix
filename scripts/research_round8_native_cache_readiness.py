import json,pathlib,subprocess,tarfile
P=pathlib.Path('/kaggle/working/hp_round7');out={}
for root in ['/kaggle/working/hp_round7','/kaggle/working/hp_round6','/kaggle/working/hp_round5']:
 p=subprocess.run(['rg','--files',root],capture_output=True,text=True)
 selected=[s for s in p.stdout.splitlines() if any(s.endswith(v) for v in ['model_opt.h','model_opt.cpp','arena_build.cpp','model_opt_forward.cpp','predictor.cpp','model_types.h'])]
 out[root]=selected[:80]
tarpath=P/'preserved/research_sources_and_candidates.tar.gz'
if tarpath.exists():
 with tarfile.open(tarpath,'r:gz') as t:
  names=[n for n in t.getnames() if n.endswith(('model_opt.h','model_opt.cpp','model_opt_forward.cpp','model_types.h'))]
  out['preserved_tar_candidate_sources']=names
  out['source_texts']={n:t.extractfile(n).read().decode('utf-8',errors='replace')[:40000] for n in names if t.getmember(n).isfile()}
print(json.dumps(out))
