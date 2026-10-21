
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
j=json.loads(project_path('research_round7_training_readiness_source_audit.json').read_text())
for x in j['source_snippets']:
 if x['path'].endswith(('train_6m.py','quantize.py','cooldown.py')):
  a=x['text'].splitlines();out=[line.strip() for line in a if any(k in line for k in ['learning_rate:', 'weight_decay=', 'momentum=', 'betas=', 'adjust_lr_fn=', 'warmup_epochs:', 'epochs:'])]
  print(json.dumps({'source':x['path'],'sha256':x['sha256'],'hyperparameters':out}))
