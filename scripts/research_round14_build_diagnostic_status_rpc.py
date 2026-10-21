from pathlib import Path
import json
W=Path('/kaggle/working/hp_round14')
for n in ('native_cpu_build_v2.json','ppmd_real_diagnostic_v1.json'):
    p=W/n
    if p.exists():print(n,p.read_text()[-12000:])
print('R13_ASSET_METADATA',[(str(p),p.stat().st_size) for p in Path('/kaggle/working/hp_round13').rglob('*') if p.is_file() and ('assets' in p.name or p.name.endswith('.bm'))][:25])
