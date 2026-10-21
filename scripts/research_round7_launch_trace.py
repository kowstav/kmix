
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

def _hp_launch_trace():
    import pathlib,subprocess,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    if not (out/'cmix_round7_trace').exists():raise RuntimeError('Trace build incomplete')
    if (out/'trace_controller.pid').exists():raise RuntimeError('Trace controller already exists')
    with (out/'trace_controller.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(out/str(project_path('research_round7_trace_controller.py')))],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'trace_controller.pid').write_text(str(p.pid))
    print(json.dumps({'pid':p.pid,'trace_build_log':(out/'build_trace.log').read_text()[-500:]}))
_hp_launch_trace()
del _hp_launch_trace
