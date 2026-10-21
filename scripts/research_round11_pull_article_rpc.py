from pathlib import Path
import json
import hashlib
import shutil
import subprocess
import time

ref='chaoscpp/hutter-r10-cpu-article-order-proxy'
S=Path('/root/hp_round11_outputs/article_order_v1')
W=Path('/kaggle/working/hp_round11/article_order_v1')
assert not S.exists() and not W.exists(), 'Inspect existing download rather than overwrite'
S.mkdir(parents=True)
result=subprocess.run(['kaggle','kernels','output',ref,'-p',str(S)],capture_output=True,text=True,timeout=35)
out={'ref':ref,'CLI_exit':result.returncode,'observed_at':time.time(),'files':[],'deletions':[]}
if result.returncode==0:
    W.mkdir(parents=True)
    for path in sorted(S.rglob('*')):
        if path.is_file():
            raw=path.read_bytes(); name=path.relative_to(S)
            target=W/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(raw)
            out['files'].append({'path':str(name),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
else:
    out['error']='Output pull failed; inspect ordinary CLI before retrying'
(Path('/kaggle/working/hp_round11')/'article_output_pull.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
for path in W.rglob('*.json') if W.exists() else []:
    if path.stat().st_size<30000: print(str(path),path.read_text())
