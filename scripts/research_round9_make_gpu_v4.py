
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
s=project_path('research_round9_core_layer_gpu_worker_v3.py').read_text().replace('core_layer_gpu_v3','core_layer_gpu_v4')
anchor="m['native_integer_linear_sites']=install(model)"
assert s.count(anchor)==1
s=s.replace(anchor,anchor+"\n from research_round9_native_rms import rms_norm\n tfh.M.rms_norm=rms_norm\n from fla.ops.kda.fused_recurrent import fused_recurrent_kda\n tfh.M.chunk_kda=fused_recurrent_kda\n m['fidelity_extensions']=['native8lane RMS order','native integer linear','correctly rounded FP32 division','fused recurrent KDA inference']")
project_path('research_round9_core_layer_gpu_worker_v4.py').write_text(s)
