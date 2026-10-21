
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

def _hp_round7_launch_build():
    import pathlib,subprocess,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    with (out/'build_lab.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(out/str(project_path('research_round7_build_lab_worker.py')))],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'build_lab.pid').write_text(str(p.pid))
    print(json.dumps({'pid':p.pid,'log':str(out/'build_lab.log')}))
_hp_round7_launch_build()
del _hp_round7_launch_build
