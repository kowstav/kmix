
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
import argparse,hashlib,json,subprocess,zipfile,sys,time,traceback
p=argparse.ArgumentParser();p.add_argument('--role',required=True,choices=['a','b']);args=p.parse_args()
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_guard_match_confirm_dispatch_'+args.role)
receipt=W/('guard_match_confirm_'+args.role+'_dispatch_v8.json')
assert not R.exists() and not receipt.exists(),'inspect existing receipt; do not duplicate'
R.mkdir();M={'status':'VERIFYING','role':args.role,'started':time.time(),'deletions':[],'paid_usd':0,'GPU':False}
def save():receipt.write_text(json.dumps(M,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
    save();prep=json.loads((W/'prepared_guard_match_confirm_v8.json.dat').read_text())
    assert prep['source_sha256']=='df8d5b7aaf8d9667a85ffe97f7671aca09e661bfe8df5402ef3f03fc607f4817'
    assert sha(W/'sources_guard_match_confirm_v8.zip.dat')==prep['source_sha256']
    gate=json.loads((W/'guard_storage_parity_v2/manifest.json').read_text())
    assert gate['status']=='PASS_64K_GUARD_RAW_PACKED_SLIM_UPX_PARITY_AND_NEUTRAL_UPX'
    previous='chaoscpp/hutter-r14-guard-match-'+('development' if args.role=='a' else 'confirm-a')+'-v1'
    q=subprocess.run(['kaggle','kernels','status',previous],capture_output=True,text=True,timeout=30)
    assert q.returncode==0 and 'KernelWorkerStatus.COMPLETE' in q.stdout
    with zipfile.ZipFile(W/'sources_guard_match_confirm_v8.zip.dat') as z:
        for e in json.loads(z.read('source_manifest.json')):
            p=(R/'code'/e['path']).resolve();assert p.is_relative_to(R);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    sys.path.insert(0,str(R/'code'));from hutter_research.dispatch_contracts import parse_successful_push
    with zipfile.ZipFile(W/'kernels_guard_match_confirm_v8.zip.dat') as z:
        for name in z.namelist():assert (R/name).resolve().is_relative_to(R)
        z.extractall(R)
    job=next(j for j in prep['jobs'] if j['role']==args.role);folder=R/job['folder'];assert sha(folder/'main.py')==job['main_sha256']
    meta=json.loads((folder/'kernel-metadata.json').read_text());assert meta['is_private'] and not meta['enable_gpu'] and not meta['enable_internet']
    q=subprocess.run(['kaggle','kernels','list','--mine','--search',job['folder'],'--csv'],capture_output=True,text=True,timeout=30)
    assert q.returncode==0 and job['ref'] not in q.stdout
    q=subprocess.run(['kaggle','kernels','push','-p',str(folder)],capture_output=True,text=True,timeout=120)
    assert q.returncode==0,'push failed: inspect, no retry'
    verified=parse_successful_push(q.stdout,'chaoscpp');assert verified['actual_ref']==job['ref']
    M.update(status='COMPLETE_VERIFIED_PRIVATE_CPU_PUSH',job=job,verified_push=verified,finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED_NO_RETRY',error=repr(e),traceback=traceback.format_exc());save();raise
