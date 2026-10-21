
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
import hashlib,json,subprocess,sys,time,zipfile
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_code_v2');Path('/root/.config/kaggle').mkdir(parents=True,exist_ok=True)
if not R.exists():
    R.mkdir()
    with zipfile.ZipFile(W/'sources_v2.zip.dat') as z:
        for row in json.loads(z.read('source_manifest.json')):
            p=(R/row['path']).resolve();assert p.is_relative_to(R)
            data=z.read(row['path']);assert hashlib.sha256(data).hexdigest()==row['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
sys.path.insert(0,str(R));from hutter_research.dispatch_contracts import parse_successful_push
ref='chaoscpp/hutter-r14-article-order-ppmd-v1';target=Path('/root/r14_order_dispatch');record=W/'article_order_submission_v1.json'
assert not record.exists() and not target.exists();target.mkdir()
# Existing runs demonstrably completed; this is a newly available ordinary slot.
done=subprocess.run(['kaggle','kernels','status','chaoscpp/hutter-r14-constructor-confirmation-v1'],capture_output=True,text=True,timeout=30)
assert done.returncode==0 and 'KernelWorkerStatus.COMPLETE' in done.stdout
check=subprocess.run(['kaggle','kernels','list','--mine','--search','hutter-r14-article-order-ppmd-v1','--csv'],capture_output=True,text=True,timeout=30)
assert check.returncode==0 and ref not in check.stdout,'resource already exists or unavailable; inspect instead'
with zipfile.ZipFile(W/'kernels_v2.zip.dat') as z:
    for name in ('main.py','kernel-metadata.json'):(target/name).write_bytes(z.read('article-order-ppmd/'+name))
assert hashlib.sha256((target/'main.py').read_bytes()).hexdigest()=='5de1e93bd838405f38e0936ca210d09b37e4655246c749a9aea11038b921ea06'
p=subprocess.run(['kaggle','kernels','push','-p',str(target)],capture_output=True,text=True,timeout=35)
r={'time':time.time(),'ref':ref,'exit':p.returncode,'previous_limit':'5 simultaneous committed CPU jobs; a completed job freed a slot'}
try:r['verified_push']=parse_successful_push(p.stdout,'chaoscpp') if p.returncode==0 else None
except ValueError:r['verified_push']=None
if not r['verified_push']:r['error']=(p.stdout+p.stderr)[-1800:]
record.write_text(json.dumps(r,indent=2));print(json.dumps(r))
