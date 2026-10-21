from pathlib import Path
import ast,base64,hashlib,json,zipfile
R=Path(__file__).resolve().parent;O=R/'kaggle_cpu_round14';archive=O/'sources_v2.zip';assert not archive.exists();entries=[]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
    files=list((R/'hutter_research').rglob('*'))+[R/'tests/test_group_weight_storage.py',R/'tests/test_article_order_ppmd.py']
    for p in sorted(files):
        if not p.is_file() or p.suffix not in ('.py','.h','.cpp','.inc') or '__pycache__' in p.parts:continue
        raw=p.read_bytes();name=p.relative_to(R).as_posix()
        if p.suffix=='.py':ast.parse(raw.decode())
        z.writestr(name,raw);entries.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    z.writestr('source_manifest.json',json.dumps(entries,indent=2))
blob=archive.read_bytes();digest=hashlib.sha256(blob).hexdigest();jobs=[]
for kind,module,internet in [('group-weight-storage','cpu_round14_group_storage',False),('article-order-ppmd','cpu_round14_order',True)]:
    folder=O/kind;folder.mkdir()
    text="""import base64,hashlib,io,json,os,subprocess,sys,zipfile
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
raw=base64.b64decode(__BLOB__);assert hashlib.sha256(raw).hexdigest()==__SHA__
root=Path('/root/r14_code_v2');root.mkdir()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for r in json.loads(z.read('source_manifest.json')):
        p=(root/r['path']).resolve();assert p.is_relative_to(root)
        data=z.read(r['path']);assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
sys.path.insert(0,str(root))
if __PPMD__:
    with open('/kaggle/working/pyppmd_install.log','w') as log:
        subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check','--target','/root/r14_pyppmd','pyppmd==1.3.1'],stdout=log,stderr=subprocess.STDOUT,timeout=300,check=True)
    sys.path.insert(0,'/root/r14_pyppmd')
from hutter_research.__MODULE__ import main
if __name__=='__main__':main()
""".replace('__BLOB__',repr(base64.b64encode(blob).decode())).replace('__SHA__',repr(digest)).replace('__PPMD__',repr(internet)).replace('__MODULE__',module)
    ast.parse(text);(folder/'main.py').write_bytes(text.encode());ref='chaoscpp/hutter-r14-'+kind+'-v1'
    metadata={'id':ref,'title':ref.split('/')[1],'code_file':'main.py','language':'python','kernel_type':'script','is_private':True,
      'enable_gpu':False,'enable_tpu':False,'enable_internet':internet,'dataset_sources':['chaoscpp/hutter-r13-four-lane-cpu-assets-v1'],
      'competition_sources':[],'kernel_sources':[]}
    (folder/'kernel-metadata.json').write_bytes(json.dumps(metadata,indent=2).encode())
    jobs.append({'ref':ref,'folder':kind,'worker_count':4,'main_sha256':hashlib.sha256(text.encode()).hexdigest(),'internet':internet})
with zipfile.ZipFile(O/'kernels_v2.zip','x',zipfile.ZIP_DEFLATED) as z:
    for job in jobs:
        for p in (O/job['folder']).iterdir():z.write(p,p.relative_to(O).as_posix())
(O/'prepared_v2.json').write_text(json.dumps({'jobs':jobs,'sources_sha256':digest,'entries':entries},indent=2))
print(json.dumps({'jobs':jobs,'sources_sha256':digest}))
