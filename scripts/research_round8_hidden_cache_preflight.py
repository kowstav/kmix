
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

import json,pathlib,subprocess,hashlib
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'hidden_cache_v3_preflight';D.mkdir(exist_ok=False)
with (D/'compile.log').open('x') as f:subprocess.run(['g++','-O3','-march=x86-64-v3','-mrecip=none','-std=c++17',str(R/str(project_path('research_round8_hidden_cache_replay_v3.cpp'))),'-o',str(D/'replay')],check=True,stdout=f,stderr=subprocess.STDOUT)
p=subprocess.run([str(D/'replay'),'selftest'],check=True,capture_output=True,text=True);(D/'selftest.log').write_text(p.stdout);m={'status':'PASS','source_sha256':hashlib.sha256((R/'research_round8_hidden_cache_replay_v3.cpp').read_bytes()).hexdigest(),'binary_sha256':hashlib.sha256((D/'replay').read_bytes()).hexdigest(),'selftest':json.loads(p.stdout)};(D/'manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps(m))
