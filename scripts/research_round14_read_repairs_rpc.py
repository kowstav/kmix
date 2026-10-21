from pathlib import Path
import json,sys,inspect
W=Path('/kaggle/working/hp_round14')
for n in ('ppmd_diagnostic_v1.json','compiler_restore_v1.json','native_cpu_build_v1.json','tail_collection_v1.json'):
    p=W/n
    if p.exists():print(n,p.read_text()[-6500:])
sys.path.insert(0,'/root/r14_ppmd_diagnostic/lib')
import pyppmd
for name in ('compress','_compress8','_decompress8'):
    print(name,inspect.getsource(getattr(pyppmd,name)))
