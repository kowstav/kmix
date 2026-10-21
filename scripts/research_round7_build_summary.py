
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

import pathlib,json
root=project_root(__file__)
rows=[]
for name in 'abcd':
    row={'slice':name}
    for mode in ['balanced','edit']:
        p=project_path(f'research_round7_{name}_corrected_{mode}_screen.json', base=root)
        if p.exists():row[mode]=json.loads(p.read_text())['scores']['combined']['prequential_saving_bytes']
    for mode in ['exact','edit','masked_edit']:
        p=project_path(f'research_round7_{name}_line_{mode}.json', base=root)
        if p.exists():row['line_'+mode]=json.loads(p.read_text())['score']['prequential_saving_bytes']
    for tag in ['word_context_atlas','calibration_screen']:
        p=project_path(f'research_round7_{name}_{tag}.json', base=root)
        if p.exists():row[tag]=json.loads(p.read_text())
    rows.append(row)
(project_path('research_round7_summary.json', base=root)).write_text(json.dumps(rows,indent=2))
for row in rows:print({k:round(v,9) if isinstance(v,float) else v for k,v in row.items() if k not in ['word_context_atlas','calibration_screen']})
for tag in ['word_context_atlas','calibration_screen']:
    p=project_path('research_round7_b_'+tag+'.json', base=root)
    if p.exists():print(tag,p.read_text()[:4500])
