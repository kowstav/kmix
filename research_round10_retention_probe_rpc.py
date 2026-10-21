import pathlib,json,os,shutil
W=pathlib.Path('/kaggle/working');out={'critical':{},'small_files':{},'large_files':[]}
for p in [W/'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt',W/'hp_round7/lex_audit/lex_h1_run11.tfwc2',W/'hp_round7/preserved/data/vocab.bm']:
 out['critical'][str(p)]={'exists':p.exists(),'symlink':p.is_symlink(),'bytes':p.stat().st_size if p.exists() else None}
for root in [W/'hp_round9',W/'hp_round7/preserved']:
 if not root.exists():continue
 for p in root.rglob('*'):
  if not p.is_file():continue
  if p.is_symlink():continue
  size=p.stat().st_size
  if size>10_000_000:out['large_files'].append({'path':str(p),'bytes':size})
  if p.suffix in ['.tfwc2','.tfwc3','.bin','.cmx'] and 'native' in str(p):out['small_files'][str(p)]=size
out['root_scratch']=pathlib.Path('/root/hp_round9').exists()
print(json.dumps(out))
