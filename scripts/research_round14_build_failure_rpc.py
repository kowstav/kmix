from pathlib import Path
import sys,inspect,json
W=Path('/kaggle/working/hp_round14');p=W/'native_cpu_build_neutral.log';print('BUILD',p.read_text(errors='replace')[-6000:])
sys.path.insert(0,'/root/r14_ppmd_diagnostic/lib');import pyppmd;print(inspect.getsource(pyppmd._decompress8))
print('RAW_CANDIDATES',[str(p) for p in Path('/kaggle/working').glob('**/*enwik9*') if p.is_file()][:50])
