from pathlib import Path
import json,urllib.request
S=Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree')
out={}
for name in ('makefile','src/predictor.cpp','src/predictor.h','src/models/ppmd.h','src/models/ppmd.cpp'):
    p=S/name
    if p.exists():out[name]=p.read_text()
try:
    r=urllib.request.urlopen('https://apt.llvm.org/jammy/dists/llvm-toolchain-jammy-17/Release',timeout=15)
    out['official_llvm17_repository']={'HTTP':r.status,'metadata':r.read(1200).decode()}
except Exception as e:out['official_llvm17_repository']={'error':repr(e)}
Path('/kaggle/working/hp_round13/build_probe.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'record':'hp_round13/build_probe.json','source_files':list(out),'LLVM17':out['official_llvm17_repository']}))
