
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

import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'error_memory_preflight_v1';D.mkdir(exist_ok=False)
p=subprocess.run(['g++','-O3','-march=x86-64-v3','-mrecip=none','-std=c++17',str(R/str(project_path('research_round8_error_memory.cpp'))),'-o',str(D/'replay')],capture_output=True,text=True);(D/'compile.log').write_text(p.stdout+p.stderr)
if p.returncode:print(json.dumps({'status':'COMPILE_FAIL','tail':p.stderr[-2600:]}))
else:
 p=subprocess.run([str(D/'replay'),'selftest'],capture_output=True,text=True);(D/'selftest.log').write_text(p.stdout+p.stderr);print(json.dumps({'status':'PASS' if not p.returncode else 'SELFTEST_FAIL','output':p.stdout+p.stderr}))
