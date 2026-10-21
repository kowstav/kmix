
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
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'semantic_replay_v1';graph=R/'semantic_graph_v1/manifest.json'
g=json.loads(graph.read_text());assert g['status']=='COMPLETE_GRAPH_NOT_COMPRESSION_RESULT',g['status']
if D.exists():print(json.dumps({'reused':True,'manifest':json.loads((D/'manifest.json').read_text())}))
else:
 with (R/'semantic_replay_v1_controller.log').open('x') as log:p=subprocess.Popen(['python',str(R/str(project_path('research_round8_semantic_replay_worker.py')))],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps({'launched':True,'pid':p.pid,'path':str(D)}))
