
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
r=json.loads(project_path('research_round7_session355529591_source_readiness.json').read_text())
for name,text in r['source'].items():
 print('\nFILE',name)
 if name.endswith(('make_training_data.sh','preprocess_roundtrip.cpp','preprocessor.h')):print(text[:15500])
 elif name.endswith('runner.cpp'):
  lines=text.splitlines()
  for i,l in enumerate(lines):
   if any(t in l for t in ('Usage','preprocess_only','Preprocess','argc','strcmp(argv','Generate','case \'p\'')):
    print('\n'.join(lines[max(0,i-3):i+12]))
 elif name.endswith('genprobs.py'):print(text[:3500])
