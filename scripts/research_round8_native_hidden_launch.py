
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

import pathlib,subprocess,json,os
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'native_hidden_trace_v1';assert not D.exists(),'Existing experiment: inspect and reuse'
log=(R/'native_hidden_trace_v1_controller.log').open('x');p=subprocess.Popen(['python','-u',str(R/str(project_path('research_round8_native_hidden_trace_worker.py')))],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'launched_pid':p.pid,'experiment':'native_hidden_trace_v1','retraining':False,'paid_rental_usd':0,'deletions':[]}))
