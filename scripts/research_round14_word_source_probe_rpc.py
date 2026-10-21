from pathlib import Path
import json
W=Path('/kaggle/working');out={}
for name in ('hp_round11/word_events.cpp','hp_round12_claude/warm_fallback/manifest.json'):
    p=W/name
    if p.exists():out[name]=p.read_text()
out['native_binaries']=[str(p.relative_to(W)) for p in (W/'hp_round13/native_binaries_v1').glob('*')]
print(json.dumps(out))
