from pathlib import Path
p=Path('research_round9_core_layer_gpu_worker_v2.py')
s=p.read_text().replace('core_layer_gpu_v2','core_layer_gpu_v3').replace('from research_round9_native_integer_linear import install','from research_round9_native_integer_linear_v2 import install')
Path('research_round9_core_layer_gpu_worker_v3.py').write_text(s)
s=Path('research_round9_launch_core_layer_gpu_v2_rpc.py').read_text().replace('core_layer_gpu_v2','core_layer_gpu_v3')
Path('research_round9_launch_core_layer_gpu_v3_rpc.py').write_text(s)
