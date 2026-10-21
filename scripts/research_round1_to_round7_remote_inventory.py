"""Read-only check for the missing early experiment ledger in the current session."""
import json
from pathlib import Path

roots=[Path('/kaggle/working/hutter_lab'),Path('/root/hutter_lab'),Path('/root/hp'),
       Path('/kaggle/input'),Path('/kaggle/working')]
out={}
for root in roots:
    if not root.exists():
        out[str(root)]={'exists':False}
        continue
    entries=[]
    for p in sorted(root.iterdir())[:100]:
        entries.append({'name':p.name,'directory':p.is_dir(),
                        'bytes':p.stat().st_size if p.is_file() else None})
    out[str(root)]={'exists':True,'entries':entries}
early=[]
for root in roots[:2]:
    if not root.exists():continue
    for pattern in ('*.json','*.md','*.txt','exp1/*.json','exp1/*.md','logs/*.txt','results/*.json'):
        early.extend(str(p) for p in root.glob(pattern) if p.is_file())
out['early_ledger_candidates']=sorted(set(early))[:150]
print(json.dumps(out))
