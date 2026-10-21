
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
R=project_root(__file__);O=project_path('kaggle_cpu_round14', base=R);O.mkdir(exist_ok=True)
zpath=O/'sources_v1.zip';assert not zpath.exists();entries=[]
with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED) as z:
    files=list((project_path('hutter_research', base=R)).rglob('*'))+[project_path('research_round14_full_verify_worker.py', base=R)]
    for p in sorted(files):
        if not p.is_file() or p.suffix not in ('.py','.cpp','.h','.inc') or '__pycache__' in p.parts:continue
        raw=p.read_bytes();name=p.relative_to(R).as_posix()
        if p.suffix=='.py':ast.parse(raw.decode())
        z.writestr(name,raw);entries.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    z.writestr('source_manifest.json',json.dumps(entries,indent=2))
blob=zpath.read_bytes();digest=hashlib.sha256(blob).hexdigest();jobs=[]
for kind,module,arg in [('constructor-development','cpu_round14_constructor','development'),('constructor-confirmation','cpu_round14_constructor','confirmation'),
                        ('native-confirmation-a','cpu_round14_native_confirmation','a'),('native-confirmation-b','cpu_round14_native_confirmation','b')]:
    folder=O/kind;folder.mkdir()
    text="""import base64,hashlib,io,json,os,sys,zipfile
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
raw=base64.b64decode(__BLOB__);assert hashlib.sha256(raw).hexdigest()==__SHA__
root=Path('/root/r14_code_v1');root.mkdir()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for r in json.loads(z.read('source_manifest.json')):
        p=(root/r['path']).resolve();assert p.is_relative_to(root)
        data=z.read(r['path']);assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
sys.path.insert(0,str(root))
from hutter_research.__MODULE__ import main
if __name__=='__main__':main(__ARG__)
""".replace('__BLOB__',repr(base64.b64encode(blob).decode())).replace('__SHA__',repr(digest)).replace('__MODULE__',module).replace('__ARG__',repr(arg))
    ast.parse(text);(folder/'main.py').write_bytes(text.encode());ref='chaoscpp/hutter-r14-'+kind+'-v1'
    datasets=['chaoscpp/hutter-r13-four-lane-cpu-assets-v1']
    if kind.startswith('native'):datasets.append('chaoscpp/hutter-r13-native-final-head-assets-v2')
    metadata={'id':ref,'title':ref.split('/')[1],'code_file':'main.py','language':'python','kernel_type':'script','is_private':True,
       'enable_gpu':False,'enable_tpu':False,'enable_internet':False,'dataset_sources':datasets,'competition_sources':[],'kernel_sources':[]}
    (folder/'kernel-metadata.json').write_bytes(json.dumps(metadata,indent=2).encode())
    jobs.append({'ref':ref,'folder':kind,'worker_count':4,'main_sha256':hashlib.sha256(text.encode()).hexdigest()})
with zipfile.ZipFile(O/'kernels_v1.zip','x',zipfile.ZIP_DEFLATED) as z:
    for r in jobs:
        for p in (O/r['folder']).iterdir():z.write(p,p.relative_to(O).as_posix())
(O/'prepared_v1.json').write_text(json.dumps({'jobs':jobs,'sources_sha256':digest,'entries':entries},indent=2))
print(json.dumps({'jobs':jobs,'sources_sha256':digest}))
