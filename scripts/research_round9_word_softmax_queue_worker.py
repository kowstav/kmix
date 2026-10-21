"""Launch once after current GPU1 training finishes; no overlapping jobs."""

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

import pathlib,json,time,os,subprocess,traceback
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'word_softmax_queue_v1';D.mkdir(exist_ok=False);m={'status':'WAITING','pid':os.getpid(),'started':time.time(),'dependency':'core_extension_v1','child_launched':False}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
try:
 save('waiting for existing GPU1 selected-core finetuning, no duplicate GPU allocation')
 while True:
  j=json.loads((R/'core_extension_v1/manifest.json').read_text())
  if j['status'].startswith('COMPLETE'):break
  if j['status']=='FAIL':raise RuntimeError(j.get('error'))
  assert time.time()-m['started']<7200,'dependency still incomplete after2hours'
  time.sleep(30)
 assert not (R/'word_softmax_v1').exists();p=subprocess.Popen(['python3',str(R/str(project_path('research_round9_word_softmax_worker.py')))],stdout=(R/'word_softmax_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);m.update(status='COMPLETE_DISPATCHED',child_launched=True,child_pid=p.pid,finished=time.time());save('exact word-softmax/composer job dispatched once on GPU1')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('queue failure preserved');raise
