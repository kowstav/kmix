
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
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'core_setup_v1').exists()
p=subprocess.Popen(['python3',str(R/str(project_path('research_round9_core_setup_worker.py')))],stdout=(R/'core_setup_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
(R/'core_setup_launch.json').write_text(json.dumps({'pid':p.pid,'session':355735431}));print(json.dumps({'pid':p.pid}))
