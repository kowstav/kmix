"""Stream full entry SHA/CRC verification without extracting or deleting content."""

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

import pathlib,json,hashlib,zipfile,datetime
P=project_root(__file__)
def sha(file):
 h=hashlib.sha256()
 with file.open('rb') as f:
  while chunk:=f.read(1<<20):h.update(chunk)
 return h.hexdigest()
meta=json.loads((project_path('research_round9_compact_download_parts_v2_results.json', base=P)).read_text(encoding='utf-8-sig'))
p=project_path('research_round9_extended_evidence_v2.zip', base=P);assert p.stat().st_size==meta['source_bytes'];assert sha(p)==meta['source_sha256']
with zipfile.ZipFile(p) as z:
 rows=json.loads(z.read('bundle_entry_manifest.json'));assert len(z.namelist())==len(rows)+1
 for row in rows:
  h=hashlib.sha256();n=0
  with z.open(row['file']) as f:
   while chunk:=f.read(1<<20):h.update(chunk);n+=len(chunk)
  assert n==row['bytes'] and h.hexdigest()==row['sha256'],row['file']
result={'status':'LOCAL_FULL_ZIP_CRC_AND_EVERY_ENTRY_SHA_PASS','bytes':p.stat().st_size,'sha256':meta['source_sha256'],'entries':len(rows)+1,'source_entries':len(rows),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deletions':[]}
(project_path('research_round9_extended_evidence_v2_validation.json', base=P)).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
