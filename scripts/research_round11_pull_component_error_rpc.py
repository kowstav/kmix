from pathlib import Path
import json
import hashlib
import subprocess
import time

ref='chaoscpp/hutter-r10-cpu-component-ppmd'
S=Path('/root/hp_round11_outputs/component_ppmd_v1')
W=Path('/kaggle/working/hp_round11/component_ppmd_v1')
assert not S.exists() and not W.exists(), 'Inspect existing output pull'
S.mkdir(parents=True)
p=subprocess.run(['kaggle','kernels','output',ref,'-p',str(S)],capture_output=True,text=True,timeout=35)
out={'ref':ref,'CLI_exit':p.returncode,'observed_at':time.time(),'files':[],'deletions':[]}
if p.returncode==0:
    W.mkdir(parents=True)
    for path in sorted(S.rglob('*')):
        if path.is_file():
            raw=path.read_bytes(); name=path.relative_to(S)
            target=W/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(raw)
            out['files'].append({'path':str(name),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
            if name.name=='manifest.json': out['experiment_manifest']=json.loads(raw)
else: out['error']='Ordinary output API failed; do not relaunch or infer missing artifacts'
Path('/kaggle/working/hp_round11/component_output_pull.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
