from pathlib import Path
import json
W=Path('/kaggle/working/hp_round14')
for n in ('ppmd_backend_probe_v2.json','native_cpu_preflight_v1/manifest.json','native_dispatch_v3.json','native_cpu_asset_v1.json'):
    p=W/n
    if p.exists():
        m=json.loads(p.read_text());print(n,json.dumps(m if n.startswith('ppmd') else {k:v for k,v in m.items() if k not in ('cases','files')}))
