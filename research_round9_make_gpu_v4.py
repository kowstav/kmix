from pathlib import Path
s=Path('research_round9_core_layer_gpu_worker_v3.py').read_text().replace('core_layer_gpu_v3','core_layer_gpu_v4')
anchor="m['native_integer_linear_sites']=install(model)"
assert s.count(anchor)==1
s=s.replace(anchor,anchor+"\n from research_round9_native_rms import rms_norm\n tfh.M.rms_norm=rms_norm\n from fla.ops.kda.fused_recurrent import fused_recurrent_kda\n tfh.M.chunk_kda=fused_recurrent_kda\n m['fidelity_extensions']=['native8lane RMS order','native integer linear','correctly rounded FP32 division','fused recurrent KDA inference']")
Path('research_round9_core_layer_gpu_worker_v4.py').write_text(s)
