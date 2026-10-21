
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
R=project_root(__file__);O=project_path('kaggle_cpu_round14', base=R);zpath=O/'sources_guard_match_v6.zip';assert not zpath.exists();entries=[]
with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((project_path('hutter_research', base=R)).rglob('*')):
        if not p.is_file() or p.suffix not in ('.py','.cpp','.h','.hpp','.inc') or '__pycache__' in p.parts:continue
        b=p.read_bytes();n=p.relative_to(R).as_posix()
        if p.suffix=='.py':ast.parse(b.decode('utf-8'))
        z.writestr(n,b);entries.append({'path':n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    z.writestr('source_manifest.json',json.dumps(entries,indent=2))
b=zpath.read_bytes();digest=hashlib.sha256(b).hexdigest();slug='hutter-r14-guard-match-development-v1';d=O/slug;d.mkdir()
main="""import os,sys,base64,hashlib,json,io,zipfile
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
b=base64.b64decode(__BLOB__);assert hashlib.sha256(b).hexdigest()==__SHA__
r=Path('/root/r14_guard_match_code');r.mkdir()
with zipfile.ZipFile(io.BytesIO(b)) as z:
 for e in json.loads(z.read('source_manifest.json')):
  p=(r/e['path']).resolve();assert p.is_relative_to(r);raw=z.read(e['path']);assert hashlib.sha256(raw).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
sys.path.insert(0,str(r))
from hutter_research.cpu_round14_guard_match import main
if __name__=='__main__':main()
""".replace('__BLOB__',repr(base64.b64encode(b).decode())).replace('__SHA__',repr(digest))
ast.parse(main);(d/'main.py').write_bytes(main.encode())
meta={'id':'chaoscpp/'+slug,'title':slug,'code_file':'main.py','language':'python','kernel_type':'script','is_private':True,'enable_gpu':False,'enable_tpu':False,'enable_internet':False,'dataset_sources':['chaoscpp/hutter-r13-four-lane-cpu-assets-v1','chaoscpp/hutter-r14-guard-match-assets-v1'],'competition_sources':[],'kernel_sources':[]}
(d/'kernel-metadata.json').write_text(json.dumps(meta,indent=2))
with zipfile.ZipFile(O/'kernel_guard_match_v6.zip','x',zipfile.ZIP_DEFLATED) as z:
    for p in d.iterdir():z.write(p,p.relative_to(O).as_posix())
j={'ref':meta['id'],'folder':slug,'main_sha256':hashlib.sha256(main.encode()).hexdigest(),'source_sha256':digest};(O/'prepared_guard_match_v6.json').write_text(json.dumps(j,indent=2));print(json.dumps(j))
