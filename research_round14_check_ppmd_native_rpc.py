from pathlib import Path
import json
p=Path('/kaggle/working/hp_round14/ppmd_native_probe_v1.json')
print(p.read_text() if p.exists() else 'not yet written')
