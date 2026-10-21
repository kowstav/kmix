from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import os
import re
import subprocess
import time

W=Path('/kaggle/working/hp_round11')
refs=['chaoscpp/hutter-r10-cpu-'+slug for slug in ['article-order-proxy','bf16-cut107-half','bf16-cut1392-zero','bf16-unweighted','component-ppmd','integer-mixer']]
def redact(raw):
    for key in ['KAGGLE_API_TOKEN','KAGGLE_KEY']:
        if os.environ.get(key): raw=raw.replace(os.environ[key],'[CREDENTIAL REDACTED]')
    return re.sub(r'(Authorization\s*[:=]\s*)([^\n]+)',r'\1[REDACTED]',raw,flags=re.I)[:2500]
def inspect(ref):
    result=subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=15)
    return {'ref':ref,'exit':result.returncode,'stdout':redact(result.stdout),'stderr':redact(result.stderr),'observed_at':time.time()}
with ThreadPoolExecutor(max_workers=3) as pool: rows=list(pool.map(inspect,refs))
out={'observed_at':time.time(),'jobs':rows,'reason':'Creation selected slugs from notebook titles; requested IDs differ from actual owner inventory','deletions':[],'paid_usd':0}
path=W/('actual_notebook_status_'+str(int(out['observed_at']))+'.json')
path.write_text(json.dumps(out,indent=2))
print(json.dumps({'record':str(path),'jobs':rows}))
