
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
p=project_path('research_round9_core_layer_gpu_worker_v2.py')
s=p.read_text().replace('core_layer_gpu_v2','core_layer_gpu_v3').replace('from research_round9_native_integer_linear import install','from research_round9_native_integer_linear_v2 import install')
project_path('research_round9_core_layer_gpu_worker_v3.py').write_text(s)
s=project_path('research_round9_launch_core_layer_gpu_v2_rpc.py').read_text().replace('core_layer_gpu_v2','core_layer_gpu_v3')
project_path('research_round9_launch_core_layer_gpu_v3_rpc.py').write_text(s)
