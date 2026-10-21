
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

import pathlib,zipfile,json,hashlib
P=project_root(__file__);source=project_path('research_round9_extended_evidence_v2.zip', base=P);dest=project_path('research_round10_old_native_models.zip', base=P)
with zipfile.ZipFile(source) as z:
 manifest={v['file']:v for v in json.loads(z.read('bundle_entry_manifest.json'))}
 files=[v for v in z.namelist() if v.startswith('native_models/') and v.endswith('.tfwc2')]
 assert len(files)==4,files
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as o:
  rows=[]
  for name in files:
   data=z.read(name);s=hashlib.sha256(data).hexdigest();assert s==manifest[name]['sha256']
   o.writestr(name,data);rows.append({'file':name,'bytes':len(data),'sha256':s})
  o.writestr('manifest.json',json.dumps(rows,indent=2))
result={'archive_bytes':dest.stat().st_size,'archive_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'entries':rows,'source_bundle_sha256':'5467487020dd54a192bafe6fb5c76e3386d8ddadbc2423ba49d924d15f7c7656'}
(project_path('research_round10_old_native_models_zip_manifest.json', base=P)).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
