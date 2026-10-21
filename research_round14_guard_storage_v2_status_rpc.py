from pathlib import Path
import json
p=Path('/kaggle/working/hp_round14/guard_storage_build_v2.json');print(p.read_text() if p.exists() else 'missing')
