
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

import pathlib, subprocess, json
out=pathlib.Path('/kaggle/working/hp_round7')
assert not (out/'lex_native_2m_recovered').exists() and not (out/'lex_native_2m_recovery_controller.log').exists(),'Refuse duplicate recovery'
running=subprocess.check_output(['ps','-eo','args'],text=True)
assert 'cmix_round7_lex_codebook ' not in running,'Inspect existing native job before launch'
with (out/'lex_native_2m_recovery_controller.log').open('w') as f:
    p=subprocess.Popen(['python','-u',str(out/str(project_path('research_round7_recover_lex_2m_controller.py')))],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'recovery_controller_pid':p.pid,'maximum_native_jobs':2,'order':'decode C/D; regenerate lost A/B archives; decode A/B','no_deletions':True}))
