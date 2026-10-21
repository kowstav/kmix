
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

import hashlib,json,zipfile
from pathlib import Path
R=project_root(__file__);D=project_path('research_round8_native_evidence/stage_observer_source', base=R);D.mkdir(exist_ok=False);archive=project_path('research_round8_stage_observer_source_evidence.zip', base=R)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None;m=json.loads(z.read('source_evidence_manifest.json'))
 for row in m['entries']:
  p=(D/row['file']).resolve();assert p.is_relative_to(D.resolve());b=z.read(row['file']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 (D/'source_evidence_manifest.json').write_text(json.dumps(m,indent=2))
print(json.dumps({'status':'PASS','files':len(m['entries']),'all_SHA256_and_CRC':'PASS','zip_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}))
