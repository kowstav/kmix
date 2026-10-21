
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

import json,pathlib
s=json.loads(project_path('research_round7_session355529591_preprocess_sources.json').read_text())['src/fx2-cmix-transformer-v1/src/runner.cpp']
for pattern in ["mode == 'x'","mode == 's'",'split4Decomp();','SavePpmdBytes(temp_path']:
 at=s.find(pattern);print(pattern,at);print(s[max(0,at-180):at+1500] if at>=0 else '')
