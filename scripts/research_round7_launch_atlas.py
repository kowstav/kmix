
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

def _hp_round7_launch_atlas():
    import pathlib, shutil, subprocess, json, os
    out=pathlib.Path('/kaggle/working/hp_round7')
    reference=out/'reference.fx2tfwc2'
    if not reference.exists(): shutil.copyfile('/root/hp/gen/.tfweights',reference)
    logs=out/'word_atlas.log'
    if (out/'word_atlas.pid').exists(): raise RuntimeError('Atlas already has a PID record; inspect before relaunch')
    with logs.open('w') as f:
        p=subprocess.Popen(['python','-u',str(out/str(project_path('research_round7_word_atlas.py'))),'--out',str(out)],stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
    (out/'word_atlas.pid').write_text(str(p.pid))
    print(json.dumps({'pid':p.pid,'log':str(logs),'weights_magic':reference.read_bytes()[:64].hex()}))
_hp_round7_launch_atlas()
del _hp_round7_launch_atlas
