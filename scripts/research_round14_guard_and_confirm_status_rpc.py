from pathlib import Path
import json
W=Path('/kaggle/working/hp_round14')
for name in ('guard_storage_build_v1.json','compiler_restore_session356740330_v2.json','confirm_a_dispatch_v5.json'):
    p=W/name
    if p.exists():print(name,p.read_text())
