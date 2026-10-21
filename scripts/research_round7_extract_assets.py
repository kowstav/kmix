
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

import json, sys
from pathlib import Path
root=project_root(__file__)
message=json.loads((project_path(sys.argv[1] if len(sys.argv)>1 else 'research_round7_assets.json', base=root)).read_text())
data=json.loads(''.join(s['text'] for s in message['streams'] if s['name']=='stdout'))
out=project_path('research_round7_sources', base=root); out.mkdir(exist_ok=True)
for name, content in data['files'].items():
    (out/Path(name).name).write_text(content,encoding='utf-8')
(out/'asset_lists.json').write_text(json.dumps(data.get('lists',{}),indent=2))
print('Extracted',len(data['files']),'source files')
