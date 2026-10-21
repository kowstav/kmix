import pathlib,tarfile,zipfile,json,hashlib
R=pathlib.Path('/kaggle/working/hp_round9');R.mkdir(exist_ok=True)
scratch=pathlib.Path('/root/hp_round9');scratch.mkdir(exist_ok=True)
archive=pathlib.Path('/kaggle/working/hp_round7/preserved/research_sources_and_candidates.tar.gz')
result={'archive':str(archive),'members':[],'restored':[]}
if archive.exists():
 with tarfile.open(archive) as f:
  members=f.getmembers();result['members']=[{'name':p.name,'bytes':p.size} for p in members if p.isfile() and (p.name.endswith(('.tch','.py','.tfwc2','.json','.toml')) or '/pysrc/' in p.name)]
  for p in members:
   if not p.isfile():continue
   if ('/pysrc/' in p.name or '/cpp_infer/' in p.name or p.name.endswith(('.tch','pyproject.toml'))):
    target=scratch/'restored'/p.name
    if '..' in pathlib.PurePosixPath(p.name).parts:raise RuntimeError('unsafe archive path')
    target.parent.mkdir(parents=True,exist_ok=True)
    with f.extractfile(p) as src:target.write_bytes(src.read())
    result['restored'].append({'path':str(target),'bytes':target.stat().st_size})
source=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree')
out=R/'native_build_dependencies_v1.zip'
assert not out.exists()
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for sub in ['src','cpp_infer','dictionary','pysrc']:
  if (source/sub).exists():
   for p in (source/sub).rglob('*'):
    if p.is_file() and p.suffix not in ['.o','.pyc'] and '__pycache__' not in p.parts:z.write(p,str(p.relative_to(source)))
 for p in source.iterdir():
  if p.is_file() and (p.suffix in ['.py','.md','.toml','.h','.cpp'] or p.name.lower() in ['makefile','license']):z.write(p,p.name)
result['source_bundle']={'path':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'entries':len(zipfile.ZipFile(out).namelist())}
(R/'dependency_restore_manifest.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'restored_count':len(result['restored']),'source_bundle':result['source_bundle'],'checkpoints':[v for v in result['members'] if v['name'].endswith('.tch')]}))
