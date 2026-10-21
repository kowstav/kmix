import hashlib,json,pathlib
R=pathlib.Path('/kaggle/working');out={}
for rel in ['hp_round7/lex_audit','hp_round7/sources','hutter_lab/configs','hutter_lab/lab']:
    p=R/rel;out[rel]=[{'name':q.name,'bytes':q.stat().st_size if q.is_file() else None} for q in sorted(p.iterdir())] if p.is_dir() else None
for rel in ['hp_round7/lex_audit/tensor_stats.json','hp_round7/full_stream_regen_v2/manifest.json']:
    p=R/rel
    if p.is_file():out[rel]=json.loads(p.read_text())
p=R/'hutter_lab/configs'
if p.is_dir():
    out['config_contents']={q.name:q.read_text() for q in p.iterdir() if q.is_file() and q.stat().st_size<200000}
(R/'hp_round8/asset_detail.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'saved':str(R/'hp_round8/asset_detail.json'),'directory_names':{k:[x['name'] for x in v] for k,v in out.items() if isinstance(v,list) and (not v or isinstance(v[0],dict) and 'name' in v[0])},'config_files':list(out.get('config_contents',{}))}))
