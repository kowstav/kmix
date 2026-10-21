
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

import datetime,json,pathlib,subprocess,time,os
R=pathlib.Path('/kaggle/working/hp_round8');S=R/'hidden_cache_v2_controller_status.json';D=R/'hidden_cache_v2'
assert not S.exists() and not D.exists(),'Reuse existing controller/results'
m={'pid':os.getpid(),'status':'WAITING_NATIVE_IDENTITY','started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deletions':[]}
def save():S.write_text(json.dumps(m,indent=2))
save();last=None
while True:
 native=json.loads((R/'native_hidden_trace_v3/manifest.json').read_text());status=native['status']
 if status!=last:m['native_stage']=native.get('stage');save();last=status
 if status=='FAIL':m.update(status='DEPENDENCY_FAILED',error=native.get('error'));save();raise RuntimeError('Native identity prerequisite failed; no cache launch')
 if status=='COMPLETE_NATIVE_HIDDEN_IDENTITY_AND_EXPORTS':break
 time.sleep(30)
assert not D.exists();m['status']='CACHE_REPLAY_AND_FIT_RUNNING';save();p=subprocess.Popen(['python','-u',str(R/str(project_path('research_round8_hidden_cache_v2_fit_worker.py')))]);m['child_pid']=p.pid;save();start=time.monotonic();_,status,u=os.wait4(p.pid,0);code=os.waitstatus_to_exitcode(status);p.returncode=code
m.update(status='COMPLETE' if code==0 else 'FAILED',returncode=code,total_child_accounting={'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'wall_seconds':time.monotonic()-start},finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
if code:raise RuntimeError('Cache experiment failed; evidence retained')
