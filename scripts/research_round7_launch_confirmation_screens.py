
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

def _hp_launch_confirmation_screens():
    import pathlib,subprocess,os,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    if (out/'corrected_confirmation_screens.pid').exists():raise RuntimeError('Confirmation scorer already exists')
    env={**os.environ,'HP_EDIT_KERNEL':str(out/'hp_edit_kernel.so'),'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
    with (out/'corrected_confirmation_screens.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(out/str(project_path('research_round7_confirmation_screens_worker.py')))],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'corrected_confirmation_screens.pid').write_text(str(p.pid));print(json.dumps({'pid':p.pid}))
_hp_launch_confirmation_screens()
del _hp_launch_confirmation_screens
