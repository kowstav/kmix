"""Freeze self-contained source and five private four-worker CPU notebooks."""

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

ROOT=project_root(__file__)
OUT=project_path('kaggle_cpu_round13', base=ROOT);OUT.mkdir(exist_ok=True)
archive=OUT/'source_v1.zip';assert not archive.exists(),'do not replace a frozen source bundle'
entries=[]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted((project_path('hutter_research', base=ROOT)).rglob('*')):
        if not p.is_file() or p.suffix not in ('.py','.h','.cpp','.inc'):continue
        if '__pycache__' in p.parts:continue
        if p.suffix=='.py':ast.parse(p.read_text())
        raw=p.read_bytes();name=p.relative_to(ROOT).as_posix();z.writestr(name,raw)
        entries.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    z.writestr('source_manifest.json',json.dumps(entries,indent=2))
blob=archive.read_bytes();digest=hashlib.sha256(blob).hexdigest()
template='''import base64,hashlib,json,sys,zipfile,io
from pathlib import Path
JOB=__JOB__
RAW=base64.b64decode(__BLOB__)
assert hashlib.sha256(RAW).hexdigest()==__SHA__
CODE=Path('/root/r13_code');CODE.mkdir(exist_ok=False)
with zipfile.ZipFile(io.BytesIO(RAW)) as archive:
    manifest=json.loads(archive.read('source_manifest.json'))
    for row in manifest:
        target=(CODE/row['path']).resolve();assert target.is_relative_to(CODE.resolve())
        raw=archive.read(row['path']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
sys.path.insert(0,str(CODE))
from hutter_research.cpu_round13_jobs import main
if __name__=='__main__':main(JOB)
'''
rows=[]
for job in ('warm-development','warm-confirmation','constructor-descendants','weight-storage','full-corpus-factorization'):
    folder=OUT/job;folder.mkdir(exist_ok=False)
    source=template.replace('__JOB__',repr(job)).replace('__BLOB__',repr(base64.b64encode(blob).decode())).replace('__SHA__',repr(digest))
    ast.parse(source);(folder/'main.py').write_text(source,encoding='utf-8')
    ref='chaoscpp/hutter-r13-'+job+'-v1'
    metadata={'id':ref,'title':ref.split('/')[1],'code_file':'main.py','language':'python','kernel_type':'script',
      'is_private':True,'enable_gpu':False,'enable_tpu':False,'enable_internet':False,
      'dataset_sources':['chaoscpp/hutter-r13-four-lane-cpu-assets-v1'],'competition_sources':[],'kernel_sources':[]}
    (folder/'kernel-metadata.json').write_text(json.dumps(metadata,indent=2))
    rows.append({'job':job,'id':ref,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'worker_count':4})
(OUT/'prepared_manifest.json').write_text(json.dumps({'source_zip_sha256':digest,'source_zip_bytes':len(blob),'entries':entries,'jobs':rows},indent=2))
print(json.dumps({'source_zip_bytes':len(blob),'source_zip_sha256':digest,'jobs':rows}))

if __name__=='__main__':pass
