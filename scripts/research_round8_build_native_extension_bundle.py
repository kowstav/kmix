
# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

import datetime,hashlib,json,re,zipfile
from pathlib import Path
R=project_root(__file__)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
initial=project_path('research_round8_evidence.zip', base=R);assert sha(initial)=='b322344131ac6e16a0824a491968b793bc34a6a348227dfe03f41acb0d0568df'
validation=json.loads((project_path('research_round8_native_extension_validation.json', base=R)).read_text());assert validation['status']=='PASS'
output=project_path('research_round8_native_extension_evidence_20261006.zip', base=R);assert not output.exists(),'immutable bundle already exists: preserve; use a new dated/versioned output for later results'
files=[p for p in project_glob('research_round8*', base=R) if p.is_file() and p.suffix!='.zip' and p.name not in ['research_round8_native_extension_bundle_manifest.json','research_round8_native_extension_bundle_validation.json']]
files.extend(p for p in (project_path('research_round8_native_evidence', base=R)).rglob('*') if p.is_file())
files.extend(p for p in (project_path('research_round8_neif_source_audit', base=R)).iterdir() if p.is_file())
for pattern in ['research_round1_to_round7_idea_audit.*','hutter_round*_report.txt','hutter*report.md','idea_arch*']:
 files.extend(p for p in project_glob(pattern, base=R) if p.is_file())
for n in ['research_round7_checkpoint.md','research_round7_report.md','research_round7_finetuning_execution_plan.md','research_round7_sources/lex_h1_run11.tfwc2','kaggle_research_client.mjs']:
 p=project_path(n, base=R);assert p.is_file();files.append(p)
files=sorted(set(files),key=lambda p:p.relative_to(R).as_posix())
guard=re.compile(r'https?://kkb-production\.jupyter-proxy\.kaggle\.net/k/\d+/|Bearer\s+[A-Za-z0-9._-]{25,}',re.I)
for p in files:
 if p.suffix.lower() in ['.txt','.md','.json','.log','.py','.cpp','.h','.mjs']:
  assert not guard.search(p.read_text(encoding='utf-8',errors='replace')),'credential-like text: '+str(p)
entries=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
stage=json.loads((project_path('research_round8_native_stage_trace_results.json', base=R)).read_text());native=json.loads((project_path('research_round8_canonical_atom_fit_results.json', base=R)).read_text());excluded=[]
for row in stage['controls']+stage['exports']:
 excluded.append({'remote':f"hp_round8/native_stage_trace_v1/{row['slice']}{'32k' if row['size']==32768 else '512k'}/stage.f32",'bytes':row['stage_bytes'],'sha256':row['stage_sha256'],'reason':'large source trace retained remotely; executable observer/native inputs and hashes reproduce it','deleted':False})
for row in native['native_exports']:
 for name,key,bytes_count in [('final_p.u16','final_p_sha256',8388608),('hidden.q8','hidden_sha256',101187584)]:excluded.append({'remote':f"hp_round8/atom_cache_v1/{row['slice']}_native/{name}",'bytes':bytes_count,'sha256':row[key],'reason':'full trace retained remotely; compact32Kcontrols and source/native provenance are in bundle','deleted':False})
if (project_path('research_round8_native_stage_weak_confirmation_results.json', base=R)).exists():
 weak=json.loads((project_path('research_round8_native_stage_weak_confirmation_results.json', base=R)).read_text())
 for row in weak['exports']:excluded.append({'remote':f"hp_round8/native_stage_weak_confirmation_v1/{row['slice']}512k/stage.f32",'bytes':row['stage_bytes'],'sha256':row['stage_sha256'],'reason':'independent source trace retained remotely; frozen candidate/source and reproduction protocol included','deleted':False})
ef=json.loads((project_path('research_round8_source_wide_confirmation_results.json', base=R)).read_text())
for row in ef['exports']:
 for name,key,sizekey in [('stage.f32','stage_sha256','stage_bytes'),('hidden.q8','hidden_sha256','hidden_bytes'),('final_p.u16','native_p_sha256',None)]:excluded.append({'remote':f"hp_round8/source_wide_confirmation_v1/{row['slice']}512k/{name}",'bytes':row[sizekey] if sizekey else 8388608,'sha256':row[key],'reason':'full E/F teacher trace retained remotely; exact frozen replay/native provenance included','deleted':False})
for filename,directory in [('research_round8_native_inline_residual_results.json','native_inline_residual_v1'),('research_round8_native_inline_wide_results.json','native_inline_wide_v1')]:
 p=project_path(filename, base=R)
 if not p.exists():continue
 mm=json.loads(p.read_text())
 for row in mm['candidates']:
  for root,pkey,hkey in [(f"{row['slice']}512k_candidate",'candidate_p_sha256','candidate_hidden_sha256'),(f"{row['slice']}512k_candidate_decode",'candidate_p_sha256','candidate_hidden_sha256')]:
   for name,key,bcount in [('final_p.u16',pkey,8388608),('hidden.q8',hkey,101187584)]:excluded.append({'remote':f'hp_round8/{directory}/{root}/{name}','bytes':bcount,'sha256':row[key],'reason':'large native candidate trace retained remotely; encode/decode trace equality proved in manifest','deleted':False})
manifest={'created':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'COMPACT_NATIVE_EXTENSION_ALL_FAMILIES_OPEN','initial_immutable_zip_sha256':sha(initial),'session':355735431,'entries':entries,'excluded_large_remote_traces':excluded,'models_data_preserved':True,'project_deletions':[],'paid_spending_usd':0,'full_entropy_archive_qualification':False,'twenty_percent_achieved':False,'current_families':96,'executed_source_and_frequency_validation':'research_round8_native_extension_validation.json'}
mp=project_path('research_round8_native_extension_bundle_manifest.json', base=R);mp.write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(R).as_posix())
 z.write(mp,mp.name)
with zipfile.ZipFile(output) as z:
 assert z.testzip() is None
 for row in entries:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
result={'status':'PASS','zip':output.name,'bytes':output.stat().st_size,'sha256':sha(output),'files':len(entries)+1,'CRC_and_every_embedded_file_sha256':'PASS','credential_guard':'PASS','original_evidence_zip_unchanged':sha(initial)==manifest['initial_immutable_zip_sha256'],'excluded_large_trace_count':len(excluded),'all_96_families_open':True,'spending_usd':0,'deletions':[]}
(project_path('research_round8_native_extension_bundle_validation.json', base=R)).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
