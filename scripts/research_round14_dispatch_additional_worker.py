
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
import hashlib,json,os,subprocess,sys,time,traceback,zipfile
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_dispatch_v2');M={'status':'CHECKING_PREFLIGHT','started':time.time(),'jobs':[],'deletions':[],'paid_usd':0,'GPU':False}
def save():(W/'dispatch_v2.json').write_text(json.dumps(M,indent=2))
try:
    assert not R.exists() and not (W/'dispatch_v2.json').exists();R.mkdir();save()
    assert json.loads((W/'preflight_v2.json').read_text())['status']=='COMPLETE_FOUR_LINUX_CORRECTNESS_TESTS'
    with zipfile.ZipFile(W/'kernels_v2.zip.dat') as z:
        for name in z.namelist():assert (R/name).resolve().is_relative_to(R)
        z.extractall(R)
    P=json.loads((W/'prepared_v2.json').read_text());sys.path.insert(0,'/root/r14_code_v2')
    from hutter_research.dispatch_contracts import parse_successful_push
    for job in P['jobs']:
        folder=R/job['folder'];assert hashlib.sha256((folder/'main.py').read_bytes()).hexdigest()==job['main_sha256']
        meta=json.loads((folder/'kernel-metadata.json').read_text());assert meta['is_private'] and not meta['enable_gpu'] and meta['enable_internet']==job['internet']
        check=subprocess.run(['kaggle','kernels','list','--mine','--search',job['ref'].split('/')[1],'--csv'],capture_output=True,text=True,timeout=40)
        assert check.returncode==0 and job['ref'] not in check.stdout,'already submitted or status unknown; do not duplicate'
        p=subprocess.run(['kaggle','kernels','push','-p',str(folder)],capture_output=True,text=True,timeout=240)
        r={**job,'exit':p.returncode}
        try:r['verified_push']=parse_successful_push(p.stdout,'chaoscpp') if p.returncode==0 else None
        except ValueError:r['verified_push']=None
        if not r['verified_push']:
            msg=p.stdout+p.stderr
            for k in ('KAGGLE_API_TOKEN','KAGGLE_KEY'):
                if os.environ.get(k):msg=msg.replace(os.environ[k],'[REDACTED]')
            r['failure']=msg[-2000:]
        M['jobs'].append(r);save();assert r['verified_push'],'unverified API response; no automatic retry or quota bypass'
    M.update(status='COMPLETE_TWO_ADDITIONAL_VERIFIED_PUSHES',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED_NO_RETRY',error=repr(e),traceback=traceback.format_exc());save();raise
