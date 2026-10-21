import os
import subprocess
import json
import re
from pathlib import Path

secret_values=[os.environ.get(key) for key in ['KAGGLE_API_TOKEN','KAGGLE_KEY'] if os.environ.get(key)]
def redact(raw):
    for value in secret_values:
        raw=raw.replace(value,'[CREDENTIAL REDACTED]')
    raw=re.sub(r'(Authorization\s*[:=]\s*)([^\n]+)',r'\1[REDACTED]',raw,flags=re.I)
    return raw[:2500]
out={}
for label,args in [('dataset_status',['datasets','status','chaoscpp/hutter-round10-private-cpu-assets-v1']),
                   ('datasets_mine',['datasets','list','--mine','--csv','--page','1'])]:
    result=subprocess.run(['kaggle',*args],capture_output=True,text=True,timeout=45)
    out[label]={'exit_code':result.returncode,'stdout':redact(result.stdout),'stderr':redact(result.stderr)}
manifest=Path('/kaggle/working/hp_round11/private_cpu_submission_manifest.json')
if manifest.exists():
    out['failed_dispatch']=json.loads(manifest.read_text())
print(json.dumps(out))
