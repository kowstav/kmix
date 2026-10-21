from pathlib import Path
import json,zipfile,hashlib,base64,ast
R=Path(__file__).resolve().parent;O=R/'kaggle_cpu_round14';zpath=O/'sources_native_v3.zip';assert not zpath.exists();entries=[]
with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((R/'hutter_research').rglob('*')):
        if p.is_file() and p.suffix in ('.py','.cpp','.h','.hpp','.inc') and '__pycache__' not in p.parts:
            b=p.read_bytes();n=p.relative_to(R).as_posix()
            if p.suffix=='.py':ast.parse(b.decode('utf-8'))
            z.writestr(n,b);entries.append({'path':n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    z.writestr('source_manifest.json',json.dumps(entries,indent=2))
b=zpath.read_bytes();digest=hashlib.sha256(b).hexdigest();jobs=[]
for arm in ('prune_word','prune_match','prune_indirect','output_fp32'):
    slug='hutter-r14-native-'+arm.replace('_','-')+'-v1';folder=O/slug;folder.mkdir()
    main="""import os,sys,zipfile,io,base64,hashlib,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
raw=base64.b64decode(__BLOB__);assert hashlib.sha256(raw).hexdigest()==__SHA__
root=Path('/root/r14_code_native_v3');root.mkdir()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for e in json.loads(z.read('source_manifest.json')):
        p=(root/e['path']).resolve();assert p.is_relative_to(root);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
sys.path.insert(0,str(root))
from hutter_research.cpu_round14_native_ablation import main
if __name__=='__main__':main(__ARM__)
""".replace('__BLOB__',repr(base64.b64encode(b).decode())).replace('__SHA__',repr(digest)).replace('__ARM__',repr(arm))
    ast.parse(main);(folder/'main.py').write_bytes(main.encode())
    meta={'id':'chaoscpp/'+slug,'title':slug,'code_file':'main.py','language':'python','kernel_type':'script','is_private':True,'enable_gpu':False,'enable_tpu':False,'enable_internet':False,
          'dataset_sources':['chaoscpp/hutter-r13-four-lane-cpu-assets-v1','chaoscpp/hutter-r14-native-cpu-assets-v1'],'competition_sources':[],'kernel_sources':[]}
    (folder/'kernel-metadata.json').write_text(json.dumps(meta,indent=2));jobs.append({'ref':meta['id'],'folder':slug,'arm':arm,'main_sha256':hashlib.sha256(main.encode()).hexdigest(),'workers':4})
with zipfile.ZipFile(O/'kernels_native_v3.zip','x',zipfile.ZIP_DEFLATED) as z:
    for j in jobs:
        for p in (O/j['folder']).iterdir():z.write(p,p.relative_to(O).as_posix())
(O/'prepared_native_v3.json').write_text(json.dumps({'jobs':jobs,'source_sha256':digest},indent=2));print(json.dumps({'jobs':jobs,'source_sha256':digest}))
