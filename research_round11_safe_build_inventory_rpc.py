from pathlib import Path
import json
import subprocess
import inspect
from kaggle.api.kaggle_api_extended import KaggleApi

T=Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree')
out={'makefile':(T/'makefile').read_text()[:18000],
     'compiler_assets':[str(p) for p in Path('/kaggle/working').rglob('*clang*') if p.is_file()][:35],
     'push_implementation':inspect.getsource(KaggleApi.kernels_push)[:14000]}
log=Path('/kaggle/working/hp_round11/warm_atlas_v2/encode.log')
if log.exists():
    with log.open('rb') as f:
        f.seek(max(0,log.stat().st_size-1500)); out['warm_log_tail']=f.read().decode(errors='replace')
print(json.dumps(out))
