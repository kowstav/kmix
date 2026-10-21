
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

from pathlib import Path
import json,zipfile,hashlib
R=project_root(__file__);M=json.loads((project_path('research_round14_detail_preservation.json', base=R)).read_text());out=[]
for r in M['bundles']:
    p=project_path('research_round14_'+Path(r['path']).name, base=R);raw=p.read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        for e in r['entries']:
            b=z.read(e['path']);assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
    out.append({'file':p.name,'sha256':r['sha256'],'entries_verified':len(r['entries'])})
(project_path('research_round14_local_detail_verification.json', base=R)).write_text(json.dumps(out,indent=2));print(json.dumps(out))
