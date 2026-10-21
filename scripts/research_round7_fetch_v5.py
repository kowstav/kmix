
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

import json,urllib.request,hashlib,pathlib
root=project_path('research_round7_sources', base=project_root(__file__))
repo='naveenbijalwan/fx4-cmix-transformer'
req=urllib.request.Request('https://api.github.com/repos/'+repo+'/commits/main',headers={'User-Agent':'hutter-compression-research'})
with urllib.request.urlopen(req,timeout=30) as r:commit=json.load(r)['sha']
files=['pysrc/weights_compress.py','cpp_infer/src/weights_io_compressed.cpp','cpp_infer/src/weights_io.h','weights_q4_context_screen.json','LICENSE']
manifest={'repository':repo,'commit':commit,'files':[]}
for file in files:
    url='https://raw.githubusercontent.com/'+repo+'/'+commit+'/'+file
    with urllib.request.urlopen(url,timeout=30) as r:data=r.read()
    name='v5_'+pathlib.Path(file).name
    (root/name).write_bytes(data)
    manifest['files'].append({'source':url,'local':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(root/'v5_fetch_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
