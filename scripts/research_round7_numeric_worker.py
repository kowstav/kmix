
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

import datetime,json,os,pathlib,subprocess,traceback
R=pathlib.Path('/kaggle/working/hp_round7');D=R/'numeric_programs_v1';assert not D.exists();D.mkdir();rows=[]
m={'status':'RUNNING','pid':os.getpid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preregistered':'six rendered-integer programs, copy weights .01/.1; all ABCD bits charged, no tuning','deletions':[],'paid_rental_usd':0}
def save():(D/'manifest.json').write_text(json.dumps(m,indent=2));(D/'results.json').write_text(json.dumps(rows,indent=2))
save()
try:
 b=D/'numeric';subprocess.run(['g++','-O3','-std=c++17',str(R/str(project_path('research_round7_numeric_programs.cpp'))),'-o',str(b)],check=True);m['binary_bytes']=b.stat().st_size;save()
 for n in 'abcd':
  raw=R/'preserved/slices'/(n+'2m.bin') if n in 'ab' else R/(n+'2m.bin');p=R/'lex_finalbit_2m_v1'/n/'final_p.u16';log=(D/(n+'.log')).open('x');proc=subprocess.Popen([str(b),str(raw),str(p),str(R/'preserved/gen/.dict'),str(D/(n+'.json'))],stdout=log,stderr=subprocess.STDOUT);_,status,u=os.wait4(proc.pid,0);log.close();assert os.waitstatus_to_exitcode(status)==0
  row=json.loads((D/(n+'.json')).read_text());row.update(slice=n,user_seconds=u.ru_utime,max_rss_kbytes=u.ru_maxrss);rows.append(row);save();print(json.dumps({'numeric_slice':n,'saving':row['mixture_saving_bytes']}),flush=True)
 m['status']='COMPLETE';save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
