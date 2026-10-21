from pathlib import Path
import os
import re
import json
import subprocess

def redact(raw):
    for key in ['KAGGLE_API_TOKEN','KAGGLE_KEY']:
        if os.environ.get(key): raw=raw.replace(os.environ[key],'[CREDENTIAL REDACTED]')
    return re.sub(r'(Authorization\s*[:=]\s*)([^\n]+)',r'\1[REDACTED]',raw,flags=re.I)[:6000]

out={}
for label,args in [('status',['kernels','status','chaoscpp/hutter-r10-article-order-proxy-v1']),
                   ('mine',['kernels','list','--mine','--search','hutter-r10','--csv']),
                   ('status_help',['kernels','status','--help'])]:
    result=subprocess.run(['kaggle',*args],capture_output=True,text=True,timeout=12)
    out[label]={'exit':result.returncode,'stdout':redact(result.stdout),'stderr':redact(result.stderr)}
Path('/kaggle/working/hp_round11/kernel_diagnostic.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
