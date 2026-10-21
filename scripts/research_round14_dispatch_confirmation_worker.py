"""Submit exactly one frozen wave. Never rerun an accepted receipt."""

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
import argparse,json,hashlib,subprocess,zipfile,sys,time,traceback
p=argparse.ArgumentParser();p.add_argument('--role',choices=['a','b'],required=True);args=p.parse_args()
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_confirm_dispatch_'+args.role);receipt=W/('confirm_'+args.role+'_dispatch_v5.json')
M={'status':'VERIFYING_FROZEN_WAVE','role':args.role,'started':time.time(),'jobs':[],'deletions':[],'GPU':False,'paid_usd':0}
def save():receipt.write_text(json.dumps(M,indent=2))
try:
    assert not R.exists() and not receipt.exists(),'existing receipt/root: inspect instead of duplicate';R.mkdir();save()
    prep=json.loads((W/'prepared_confirm_v5.json').read_text());raw=(W/'sources_confirm_v5.zip.dat').read_bytes();assert hashlib.sha256(raw).hexdigest()==prep['source_sha256']
    assert json.loads((W/'native_cpu_preflight_v1/manifest.json').read_text())['status']=='PASS_NEUTRAL_PARITY_AND_SIX_EXACT_INVERSES'
    with zipfile.ZipFile(W/'sources_confirm_v5.zip.dat') as z:
        for e in json.loads(z.read('source_manifest.json')):
            p=(R/'code'/e['path']).resolve();assert p.is_relative_to(R);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    with zipfile.ZipFile(W/'kernels_confirm_v5.zip.dat') as z:
        for name in z.namelist():assert (R/name).resolve().is_relative_to(R)
        z.extractall(R)
    sys.path.insert(0,str(R/'code'));from hutter_research.dispatch_contracts import parse_successful_push
    if args.role=='b':
        previous=json.loads((W/'confirm_a_dispatch_v5.json').read_text());assert previous['status']=='COMPLETE_FOUR_VERIFIED_PRIVATE_CPU_PUSHES'
        for row in previous['jobs']:
            q=subprocess.run(['kaggle','kernels','status',row['ref']],capture_output=True,text=True,timeout=25)
            assert q.returncode==0 and 'KernelWorkerStatus.COMPLETE' in q.stdout,'wave A not complete: do not consume extra slots or bypass quota'
    for j in [j for j in prep['jobs'] if j['role']==args.role]:
        folder=R/j['folder'];assert hashlib.sha256((folder/'main.py').read_bytes()).hexdigest()==j['main_sha256']
        meta=json.loads((folder/'kernel-metadata.json').read_text());assert meta['is_private'] and not meta['enable_gpu'] and not meta['enable_internet']
        q=subprocess.run(['kaggle','kernels','list','--mine','--search',j['ref'].split('/')[1],'--csv'],capture_output=True,text=True,timeout=35)
        assert q.returncode==0 and j['ref'] not in q.stdout,'existing ref or lookup failure: inspect instead of duplicate'
        q=subprocess.run(['kaggle','kernels','push','-p',str(folder)],capture_output=True,text=True,timeout=120)
        row={**j,'exit':q.returncode,'verified_push':None}
        try:row['verified_push']=parse_successful_push(q.stdout,'chaoscpp') if q.returncode==0 else None
        except ValueError:pass
        if not row['verified_push']:row['error']=(q.stdout+q.stderr)[-1200:]
        M['jobs'].append(row);save();assert row['verified_push'],'unverified push: no automatic retry'
    M.update(status='COMPLETE_FOUR_VERIFIED_PRIVATE_CPU_PUSHES',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED_NO_RETRY',error=repr(e),traceback=traceback.format_exc());save();raise
