import json, os, shutil, hashlib, subprocess, datetime
from pathlib import Path
R=Path('/kaggle/working/hp_round8');R.mkdir(exist_ok=True)
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'session':355655943,'roots':{},'assets':{},'tools':{},'deletions':[]}
for s in ['/kaggle/working/hutter_lab','/kaggle/working/hp_round5','/kaggle/working/hp_round6','/kaggle/working/hp_round7/preserved','/kaggle/working/hp_round7/full_stream_regen_v2','/kaggle/working/hp_round7/sources']:
 p=Path(s);out['roots'][s]=[{'name':q.name,'directory':q.is_dir(),'bytes':q.stat().st_size if q.is_file() else None} for q in sorted(p.iterdir())] if p.is_dir() else None
for n in ['g++','clang++','clang++-17','ld.lld','upx','zstd']:
 out['tools'][n]=shutil.which(n)
base=Path('/kaggle/working/hp_round7')
for n in ['preserved/slices/a2m.bin','preserved/slices/b2m.bin','c2m.bin','d2m.bin','preserved/gen/.dict','preserved/research_sources_and_candidates.tar.gz','preserved/data/enwik9.zip']:
 p=base/n
 if p.is_file():out['assets'][n]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.stat().st_size<100_000_000 else 'DEFERRED_LARGE_FILE'}
for n in ['a','b','c','d']:
 p=base/'lex_finalbit_2m_v1'/n/'final_p.u16'
 if p.is_file():out['assets'][str(p)]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
early=[]
lab=Path('/kaggle/working/hutter_lab')
if lab.is_dir():
 for pattern in ['*.json','*.md','*.txt','results/*.json','exp1/*.json']:
  for p in lab.glob(pattern):
   if p.is_file() and p.stat().st_size<2_000_000:
    early.append({'path':str(p),'bytes':p.stat().st_size,'text':p.read_text(errors='replace')})
out['early_reports']=early
u=shutil.disk_usage('/kaggle/working');out['disk']={'used':u.used,'free':u.free,'total':u.total}
(R/'session_readiness.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'saved':str(R/'session_readiness.json'),'tools':out['tools'],'assets':out['assets'],'early_reports':[{'path':x['path'],'bytes':x['bytes']} for x in early], 'roots':out['roots'],'disk':out['disk']}))
