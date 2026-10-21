
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

def _hp_launch_edit():
    import pathlib,subprocess,os,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    subprocess.run(['python',str(out/str(project_path('research_round7_edit_screen.py'))),'--self-test'],check=True)
    jobs=[]
    for name in ['a','b']:
        code=f'''import pathlib,subprocess,os
out=pathlib.Path('/kaggle/working/hp_round7')
raw=pathlib.Path('/root/hp/slices/{name}2m.bin')
cost=pathlib.Path('/root/hp/runs/lex_{name}/cost.f32')
for mode in ['balanced','edit']:
    subprocess.run(['python',str(out/'research_round7_edit_screen.py'),'--slice',str(raw),'--cost',str(cost),'--dictionary','/root/hp/gen/.dict','--mode',mode,'--json',str(out/('{name}_'+mode+'_screen.json'))],check=True)
print('EDIT_SCREEN_COMPLETE',flush=True)
'''
        script=out/(name+'_edit_worker.py'); script.write_text(code)
        env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
        with (out/(name+'_edit.log')).open('w') as log:
            p=subprocess.Popen(['python','-u',str(script)],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        (out/(name+'_edit.pid')).write_text(str(p.pid))
        jobs.append({'name':name,'pid':p.pid})
    print(json.dumps(jobs))
_hp_launch_edit()
del _hp_launch_edit
