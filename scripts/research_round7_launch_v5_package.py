
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
out=pathlib.Path('/kaggle/working/hp_round7');log=out/'v5_package.log'
if log.exists():raise RuntimeError('Refuse duplicate package worker')
p=subprocess.Popen(['python3','-u',str(out/str(project_path('research_round7_v5_package_worker.py')))],stdout=log.open('w'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_package_worker':p.pid}))
hp=pathlib.Path('/root/hp')
for name in ['src/runner.cpp','src/predictor.cpp']:
    s=(hp/'cand_final2'/name).read_text();print('CAND_LAB_REFERENCES',name,[l.strip() for l in s.splitlines() if 'LAB_' in l][:30])
print('LAB_RAW_REFERENCES',[l.strip() for l in (hp/'round7_lab/src/runner.cpp').read_text().splitlines() if 'LAB_RAW' in l])
