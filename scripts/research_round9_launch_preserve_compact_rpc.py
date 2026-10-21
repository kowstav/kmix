
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

import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'compact_preservation_v1').exists()
# Only completed word events can be included; never snapshot a changing TSV.
assert json.loads((R/'word_events_v1/manifest.json').read_text())['status']=='COMPLETE_CAUSAL_WHOLE_WORD_EVENTS'
p=subprocess.Popen(['python3',str(R/str(project_path('research_round9_preserve_compact_worker.py')))],stdout=(R/'compact_preservation_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid}))
