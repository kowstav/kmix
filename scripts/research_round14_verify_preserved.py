
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
import hashlib,json,zipfile
R=project_root(__file__);out=[]
for record in ('batch_collection_v1','paginated_collection_v2','tail_collection_v1','word_cost_summary_v2'):
    m=json.loads((project_path('research_round14_'+record+'.json', base=R)).read_text());v=m['compact'];p=project_path('research_round14_'+Path(v['path']).name, base=R)
    assert p.stat().st_size==v['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256']
    target=project_path('research_round14_batch_evidence', base=R);target.mkdir(exist_ok=True)
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None;entries=json.loads(z.read('entries.json'))
        assert len(entries)==v['entries']
        for e in entries:
            b=z.read(e['path']);assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
            dest=target/('word_costs_v2' if record=='word_cost_summary_v2' else '')/e['path'];assert dest.resolve().is_relative_to(target.resolve());dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():assert dest.read_bytes()==b
            else:dest.write_bytes(b)
    out.append({'file':p.name,'sha256':v['sha256'],'CRC_and_entries_verified':len(entries)})
(project_path('research_round14_preserved_verification.json', base=R)).write_text(json.dumps(out,indent=2));print(json.dumps(out))
