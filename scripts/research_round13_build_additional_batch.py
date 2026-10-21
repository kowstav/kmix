
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

from pathlib import Path
import ast,base64,hashlib,json,zipfile
ROOT=project_root(__file__);OUT=project_path('kaggle_cpu_round13', base=ROOT);archive=OUT/'source_v2.zip';assert not archive.exists()
rows=[]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((project_path('hutter_research', base=ROOT)).rglob('*')):
        if not p.is_file() or p.suffix not in ('.py','.h','.cpp','.inc') or '__pycache__' in p.parts:continue
        raw=p.read_bytes();name=p.relative_to(ROOT).as_posix()
        if p.suffix=='.py':ast.parse(raw.decode())
        z.writestr(name,raw);rows.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    z.writestr('source_manifest.json',json.dumps(rows,indent=2))
blob=archive.read_bytes();digest=hashlib.sha256(blob).hexdigest();jobs=[]
for job,module in (('native-final-head','cpu_round13_native'),('weight-storage-regeneration','cpu_round13_storage_regen')):
    folder=OUT/job;folder.mkdir(exist_ok=False)
    source="""import base64,hashlib,io,json,sys,zipfile
from pathlib import Path
RAW=base64.b64decode(__BLOB__)
assert hashlib.sha256(RAW).hexdigest()==__DIGEST__
ROOT=Path('/root/r13_code_v2');ROOT.mkdir()
with zipfile.ZipFile(io.BytesIO(RAW)) as z:
    for row in json.loads(z.read('source_manifest.json')):
        target=(ROOT/row['path']).resolve();assert target.is_relative_to(ROOT.resolve())
        raw=z.read(row['path']);assert hashlib.sha256(raw).hexdigest()==row['sha256'] and len(raw)==row['bytes']
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
sys.path.insert(0,str(ROOT))
from hutter_research.__MODULE__ import main
if __name__=='__main__':main()
""".replace('__BLOB__',repr(base64.b64encode(blob).decode())).replace('__DIGEST__',repr(digest)).replace('__MODULE__',module)
    ast.parse(source);(folder/'main.py').write_bytes(source.encode())
    ref='chaoscpp/hutter-r13-'+job+'-v1';assets=['chaoscpp/hutter-r13-four-lane-cpu-assets-v1']
    if job=='native-final-head':assets.append('chaoscpp/hutter-r13-native-final-head-assets-v1')
    meta={'id':ref,'title':ref.split('/')[1],'code_file':'main.py','language':'python','kernel_type':'script',
       'is_private':True,'enable_gpu':False,'enable_tpu':False,'enable_internet':False,
       'dataset_sources':assets,'competition_sources':[],'kernel_sources':[]}
    (folder/'kernel-metadata.json').write_bytes(json.dumps(meta,indent=2).encode())
    jobs.append({'ref':ref,'job':job,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'worker_count':4})
with zipfile.ZipFile(OUT/'kernels_v2.zip','x',zipfile.ZIP_DEFLATED) as z:
    for job in jobs:
        for p in (OUT/job['job']).iterdir():z.write(p,str(p.relative_to(OUT)).replace('\\','/'))
(OUT/'prepared_additional_manifest.json').write_text(json.dumps({'source_zip_sha256':digest,'entries':rows,'jobs':jobs},indent=2))
print(json.dumps({'source_bytes':len(blob),'source_sha256':digest,'jobs':jobs}))
