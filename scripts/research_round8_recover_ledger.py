
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

import hashlib, json
from pathlib import Path
R = project_root(__file__)
D = project_path('research_round8_recovered_round1', base=R)
D.mkdir(exist_ok=True)
src = json.loads((project_path('research_round8_session_readiness.json', base=R)).read_text())
rows=[]
for row in src['early_reports']:
    p=D/Path(row['path']).name
    blob=row['text'].encode()
    if p.exists():
        assert p.read_bytes()==blob, 'Do not overwrite different recovered evidence'
    else: p.write_bytes(blob)
    try: obj=json.loads(row['text'])
    except json.JSONDecodeError: obj=None
    info={'remote':row['path'],'local':str(p),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(), 'root_type':type(obj).__name__}
    if isinstance(obj,dict): info['keys']=list(obj)
    if isinstance(obj,list):
        info['rows']=len(obj)
        info['first_row_keys']=list(obj[0]) if obj and isinstance(obj[0],dict) else []
    rows.append(info)
(D/'manifest.json').write_text(json.dumps({'recovered_date':'2026-10-06','session':355655943,'files':rows,'deletions':[]},indent=2))
print(json.dumps(rows,indent=2))
