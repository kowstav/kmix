
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
import hashlib,json,shutil,subprocess,sys,time,re,traceback
W=Path('/kaggle/working/hp_round13');OUT=W/'native_delivery_repair_v2.json';S=Path('/root/hp_round13_native_assets_v2')
M={'status':'PREPARING_CONFIRMED_DELIVERY_FIX','started':time.time(),'dataset':'chaoscpp/hutter-r13-native-final-head-assets-v2','jobs':[],'deletions':[],'paid_usd':0,'GPU':False,
   'failure_evidence':str(W/'native_failure_preserved_v1.json'),'repair':'preserve source ZIP bytes using .zip.dat to avoid Kaggle dataset auto-extraction'}
def save():OUT.write_text(json.dumps(M,indent=2))
def call(args,timeout):
    r=subprocess.run(['kaggle',*args],capture_output=True,text=True,timeout=timeout);return r.returncode,r.stdout,r.stderr
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
try:
    assert not OUT.exists() and not S.exists();save()
    fail=json.loads((W/'native_failure_preserved_v1.json').read_text());assert 'native_integration_sources_v1.zip' in json.dumps(fail)
    old=Path('/root/hp_round13_additional_assets_v1');meta=json.loads((old/'r13_native_assets.json').read_text());S.mkdir()
    for name,row in meta['files'].items():
        source=old/name;assert sha(source)==row['sha256']
        destination=S/(name+'.dat' if name.endswith('.zip') else name);shutil.copyfile(source,destination)
    files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in S.iterdir()}
    assert all(not name.endswith('.zip') for name in files)
    meta['files']=files;meta['delivery_repair']=M['repair'];(S/'r13_native_assets.json').write_text(json.dumps(meta,indent=2))
    (S/'dataset-metadata.json').write_text(json.dumps({'title':'Hutter r13 native final head assets v2','id':M['dataset'],'licenses':[{'name':'other'}]}))
    code,text,error=call(['datasets','create','-p',str(S)],600);url='https://www.kaggle.com/datasets/'+M['dataset']
    assert code==0 and url in text and 'error' not in text.lower(),'private asset creation unverified; no automatic retry'
    M.update(status='WAITING_PRIVATE_ASSETS_READY',asset_files=files,dataset_url=url);save()
    ready=False
    for delay in (0,10,20,30,60,60):
        if delay:time.sleep(delay)
        code,text,error=call(['datasets','status',M['dataset']],30);assert code==0
        if re.search(r'\b(ready|complete)\b',text,re.I):ready=True;break
    assert ready
    original=Path('/root/hp_round13_additional_kernels_v1/native-final-head');folder=Path('/root/hp_round13_native_kernel_v2');shutil.copytree(original,folder)
    meta=json.loads((folder/'kernel-metadata.json').read_text());ref='chaoscpp/hutter-r13-native-final-head-v2'
    meta.update(id=ref,title=ref.split('/')[1],dataset_sources=['chaoscpp/hutter-r13-four-lane-cpu-assets-v1',M['dataset']]);(folder/'kernel-metadata.json').write_text(json.dumps(meta,indent=2))
    assert meta['is_private'] and not meta['enable_gpu'] and not meta['enable_tpu'] and not meta['enable_internet']
    code,text,error=call(['kernels','list','--mine','--search',ref.split('/')[1],'--csv'],30);assert code==0 and ref not in text
    sys.path.insert(0,'/root/hp_round13_preflight');from hutter_research.dispatch_contracts import parse_successful_push
    code,text,error=call(['kernels','push','-p',str(folder)],240)
    row={'requested_ref':ref,'CLI_exit':code,'worker_count':4,'source_sha256':sha(folder/'main.py')}
    try:row['verified_push']=parse_successful_push(text,'chaoscpp') if code==0 else None
    except ValueError:row['verified_push']=None
    M['jobs'].append(row);save();assert row['verified_push'],'API rejection/unverified; no quota bypass'
    M.update(status='COMPLETE_VERIFIED_PRIVATE_REPAIR_SUBMISSION',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED_NO_AUTOMATIC_RETRY',error=repr(e),traceback=traceback.format_exc(),finished=time.time());save();raise
