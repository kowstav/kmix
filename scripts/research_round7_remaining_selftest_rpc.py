
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

import json,pathlib,subprocess
r=pathlib.Path('/kaggle/working/hp_round7');d=r/'remaining_experts_v1';b=d/'selftest';
subprocess.run(['g++','-O2','-std=c++17',str(r/str(project_path('research_round7_remaining_selftest.cpp'))),'-o',str(b)],check=True)
result=subprocess.check_output([str(b),str(r/'preserved/gen/.dict'),str(r/str(project_path('research_round7_remaining_graph.txt'))),str(r/str(project_path('research_round7_remaining_constructors.txt')))],text=True)
(d/'selftest.json').write_text(result);print(result)
