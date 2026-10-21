
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
out=pathlib.Path('/kaggle/working/hp_round7');assert not (out/'causal_latent_v2_controller.log').exists(),'Refuse duplicate corrected screen'
with (out/'causal_latent_v2_controller.log').open('w') as f:
    p=subprocess.Popen(['python','-u',str(out/str(project_path('research_round7_causal_latent_word_v2_screen.py')))],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'corrected_causal_latent_pid':p.pid,'activation_after_complete_marker':True,'old_evidence_preserved':True}))
