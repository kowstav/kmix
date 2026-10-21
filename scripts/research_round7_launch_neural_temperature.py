
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

def _hp_launch_neural_temperature():
    import pathlib,subprocess,os,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    jobs=[]
    for name,gpu in [('a',0),('b',1),('c',0),('d',1)]:
        # Two short sequential batches, avoiding unnecessary duplicate GPU loads.
        if name in ['c','d']:continue
        env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
        with (out/(name+'_neural_temperature.log')).open('w') as log:
            p=subprocess.Popen(['python','-u',str(out/str(project_path('research_round7_neural_temperature.py'))),'--slice',name,'--out',str(out),'--device','cuda:'+str(gpu)],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        jobs.append({'slice':name,'pid':p.pid,'gpu':gpu})
    print(json.dumps(jobs))
_hp_launch_neural_temperature()
del _hp_launch_neural_temperature
