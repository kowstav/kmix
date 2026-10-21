
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
import py_compile
R=project_root(__file__)
s=(project_path('research_round8_continuous_worker.py', base=R)).read_text(encoding='utf-8')
old="records['signals'][:,5].astype(np.float64));z=ell+features@best.x"
new="records['signals'][:,5].astype(np.float64)));z=ell+features@best.x"
assert s.count(old)==1
s=s.replace(old,new).replace("'continuous_strength_v1'","'continuous_strength_v2'")
(project_path('research_round8_continuous_v2_worker.py', base=R)).write_text(s,encoding='utf-8')
l=(project_path('research_round8_continuous_launch.py', base=R)).read_text(encoding='utf-8').replace('continuous_strength_v1','continuous_strength_v2').replace('research_round8_continuous_worker.py','research_round8_continuous_v2_worker.py')
(project_path('research_round8_continuous_v2_launch.py', base=R)).write_text(l,encoding='utf-8')
py_compile.compile(str(project_path('research_round8_continuous_v2_worker.py', base=R)),doraise=True)
py_compile.compile(str(project_path('research_round8_continuous_v2_launch.py', base=R)),doraise=True)
print('PASS: repaired worker and launcher parse; v1 source and failure evidence retained')
