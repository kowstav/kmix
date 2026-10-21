from pathlib import Path
import os
import subprocess
import json
import re

secrets=[os.environ.get(key) for key in ['KAGGLE_API_TOKEN','KAGGLE_KEY'] if os.environ.get(key)]
def redacted(raw):
    for value in secrets:
        raw=raw.replace(value,'[CREDENTIAL REDACTED]')
    raw=re.sub(r'(https://[^\s?]+)\?[^\s]+',r'\1?[SIGNED QUERY REDACTED]',raw)
    return raw[:3500]
out={}
for label,args in [('empty_kernel_inventory',['kernels','list','--mine','--search','hutter-r10-article-order-proxy-v1','--csv']),
                   ('empty_dataset_inventory',['datasets','list','--mine','--search','hutter-round10-private-cpu-assets-v1','--csv'])]:
    result=subprocess.run(['kaggle',*args],capture_output=True,text=True,timeout=35)
    out[label]={'exit_code':result.returncode,'stdout':redacted(result.stdout),'stderr':redacted(result.stderr)}
folder=Path('/root/hp_round11_private_assets_v2/downloaded_dataset_verification')
out['downloads']=[{'name':p.name,'bytes':p.stat().st_size} for p in folder.glob('*') if p.is_file()]
print(json.dumps(out))
