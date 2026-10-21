
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

for source,target,old_dir,new_dir in [
 ('research_round8_resume_atom_fit_worker.py','research_round8_resume_atom_fit_worker_v2.py','atom_fit_resume_v1','atom_fit_resume_v2'),
 ('research_round8_resume_error_memory_worker.py','research_round8_resume_error_memory_worker_v2.py','error_memory_resume_v1','error_memory_resume_v2')]:
 s=Path(source).read_text().replace(old_dir,new_dir)
 s=s.replace("R/'atom_fit_resume_v1/manifest.json'","R/'atom_fit_resume_v2/manifest.json'")
 s=s.replace('json.dumps(m,indent=2)', 'json.dumps(m,indent=2,default=lambda value:value.item() if isinstance(value,np.generic) else str(value))')
 s=s.replace('def gap(t,g):return max(0.,float(g@(t-np.where(g>=0,-1,1)))/np.log(2)/8)', 'def gap(t,g):return float(max(0.,float(g@(t-np.where(g>=0,-1,1)))/np.log(2)/8))')
 # Reuse the exact design matrix within a head; avoid re-parsing features at each Newton step.
 s=s.replace('def summation(data,arm,t,hessian=False):', '_prepared_cache={}\n_prepared_arm=None\ndef summation(data,arm,t,hessian=False):')
 s=s.replace("a=rec[i:i+131072];X=columns(a,arm);l=X[:,1];y=a['y'].astype(np.float64);", "a=rec[i:i+131072];X,yy=_prepared_cache[id(rec)];X=X[i:i+131072];l=X[:,1];y=yy[i:i+131072];")
 s=s.replace('def solve(data,arm):\n', "def solve(data,arm):\n global _prepared_cache,_prepared_arm\n _prepared_cache.clear();_prepared_arm=arm\n for rec in data:_prepared_cache[id(rec)]=(columns(rec,arm),rec['y'].astype(np.float64))\n")
 assert '_prepared_cache[id(rec)]' in s
 Path(target).write_text(s)

s=project_path('research_round8_canonical_cost_atlas.py').read_text().replace("D=R/'canonical_cost_atlas_v1'","D=R/'canonical_cost_atlas_v2'")
s=s.replace("dtype='<u2').reshape(-1,8)","dtype='<u2').astype(np.int32).reshape(-1,8)")
project_path('research_round8_canonical_cost_atlas_v2.py').write_text(s)
project_path('research_round8_session355735431_repair_launch.py').write_text('''import pathlib,subprocess,json,os,signal
R=pathlib.Path('/kaggle/working/hp_round8')
# Stop only the observed waiting controller, after verifying PID and exact argv.
p=pathlib.Path('/proc/117/cmdline')
if p.exists():
 cmd=p.read_bytes().split(bytes([0]));assert str(R/'research_round8_resume_error_memory_worker.py').encode() in cmd
 m=json.loads((R/'error_memory_resume_v1/manifest.json').read_text());assert m['stage'].startswith('waiting') and not m['native_exports'] if 'native_exports' in m else m['stage'].startswith('waiting')
 os.kill(117,signal.SIGTERM)
print(json.dumps({'stopped_waiting_controller':117,'reason':'parent exited on NumPy boolean JSON serialization; preserve original failed directories and scripts','deletions':[]}))
for directory,source in [('atom_fit_resume_v2','research_round8_resume_atom_fit_worker_v2.py'),('error_memory_resume_v2','research_round8_resume_error_memory_worker_v2.py'),('canonical_cost_atlas_v2','research_round8_canonical_cost_atlas_v2.py')]:
 assert not (R/directory).exists()
 p=subprocess.Popen(['python','-u',str(R/source)],stdout=(R/(directory+'_controller.log')).open('x'),stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps({'pid':p.pid,'experiment':directory,'native_inference_reused':True,'spending_usd':0,'deletions':[]}))
''')
