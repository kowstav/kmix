
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
R=project_root(__file__)
src=(project_path('research_round8_clean_title.cpp', base=R)).read_text(encoding='utf-8')
needle='x.counts[x.ids.at("aardvark")]!=4'
assert src.count(needle)==1
# Fixture has one title occurrence plus two body occurrences, not four.
(project_path('research_round8_clean_title_v2.cpp', base=R)).write_text(src.replace(needle,'x.counts[x.ids.at("aardvark")]!=3'),encoding='utf-8')
for name in ['worker','launch']:
    s=(project_path(f'research_round8_clean_title_{name}.py', base=R)).read_text(encoding='utf-8')
    s=s.replace('clean_title_v1','clean_title_v2').replace('research_round8_clean_title.cpp','research_round8_clean_title_v2.cpp').replace('research_round8_clean_title_worker.py','research_round8_clean_title_v2_worker.py')
    if name=='worker':s=s.replace("'core_retraining':False}","'core_retraining':False,'repair':'Self-test fixture expected 4 aardvarks but contains 3; only the assertion changes. v1 source/binary/log/manifest preserved.'}")
    (project_path(f'research_round8_clean_title_v2_{name}.py', base=R)).write_text(s,encoding='utf-8')
