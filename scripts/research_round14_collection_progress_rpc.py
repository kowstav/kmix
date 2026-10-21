from pathlib import Path
import json
W=Path('/kaggle/working/hp_round14')
for name in ('native_wave_collection_v1.json','compiler_restore_session356740330_v2.json'):
    p=W/name
    if p.exists():
        m=json.loads(p.read_text())
        if 'jobs' in m:
            m['jobs']=[{k:v for k,v in r.items() if k!='files'}|{'files':len(r['files'])} for r in m['jobs']]
        print(name,json.dumps(m))
