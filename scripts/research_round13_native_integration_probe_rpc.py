from pathlib import Path
import json,subprocess
T=Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree')
names=('src/coder/encoder.cpp','src/coder/decoder.cpp','src/predictor.h','src/runner.cpp','src/mixer/sigmoid.cpp')
out={name:(T/name).read_text() for name in names}
out['files']=[str(p.relative_to(T)) for p in T.iterdir()]
out['build_profiles']=[{'path':str(p.relative_to(T)),'bytes':p.stat().st_size} for p in T.rglob('*') if p.is_file() and ('prof' in p.name or p.name.endswith('.o'))][:200]
Path('/kaggle/working/hp_round13/native_integration_probe.json').write_text(json.dumps(out))
print(json.dumps({k:v for k,v in out.items() if k!='src/runner.cpp'}))
