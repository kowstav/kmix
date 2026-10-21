
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

import datetime,hashlib,json,os,pathlib,subprocess,time,traceback
R=pathlib.Path('/kaggle/working/hp_round7');D=R/'remaining_experts_v1'
assert not D.exists(),'Never duplicate or overwrite a completed experiment'
D.mkdir();m={'status':'RUNNING','started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':os.getpid(),'experiments':['I04b','I06','I07','I08','I09 TTL screen','I12'],'deletions':[],'paid_rental_usd':0};rows=[]
def save():
 (D/'manifest.json').write_text(json.dumps(m,indent=2));(D/'results.json').write_text(json.dumps(rows,indent=2))
save()
try:
 binary=D/'replay';subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra',str(R/str(project_path('research_round7_remaining_experts.cpp'))),'-o',str(binary)],check=True)
 m['binary_bytes']=binary.stat().st_size;m['binary_sha256']=hashlib.sha256(binary.read_bytes()).hexdigest();save()
 for n,limit in [('a',32768),('b',32768),*[(s,0) for s in 'abcd']]:
  name=n+('_32k' if limit else '_2m');raw=R/'preserved/slices'/(n+'2m.bin') if n in 'ab' else R/(n+'2m.bin');p=R/'lex_finalbit_2m_v1'/n/'final_p.u16';log=(D/(name+'.log')).open('x');start=time.monotonic()
  cmd=[str(binary),str(raw),str(p),str(R/'preserved/gen/.dict'),str(R/'research_round7_remaining_graph.txt'),str(R/'research_round7_remaining_constructors.txt'),str(limit),str(D/(name+'.json'))]
  proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);pid,status,u=os.wait4(proc.pid,0);proc.returncode=os.waitstatus_to_exitcode(status);log.close()
  if proc.returncode:raise RuntimeError((name,'replay failed',proc.returncode))
  row=json.loads((D/(name+'.json')).read_text());row.update(slice=name,user_seconds=u.ru_utime,system_seconds=u.ru_stime,max_rss_kbytes=u.ru_maxrss,wall_controller=time.monotonic()-start);(D/(name+'.json')).write_text(json.dumps(row,indent=2));rows.append(row);save();print(json.dumps({'completed':name,'mixture_saving_bytes':row['mixture_saving_bytes'],'cpu':u.ru_utime}),flush=True)
 m.update(status='COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except BaseException as e:
 m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
