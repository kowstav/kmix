from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,os,re,subprocess,time
W=Path('/kaggle/working/hp_round13')
dispatch=json.loads((W/'dispatch_v1.json').read_text())
def check(row):
    ref=row['verified_push']['actual_ref']
    r=subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=25)
    text=r.stdout+r.stderr
    for key in ('KAGGLE_API_TOKEN','KAGGLE_KEY'):
        if os.environ.get(key):text=text.replace(os.environ[key],'[REDACTED]')
    return {'ref':ref,'exit':r.returncode,'status_output':text[:2000]}
with ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(check,dispatch['jobs']))
out={'observed_at':time.time(),'jobs':rows}
p=W/('notebook_status_'+str(int(out['observed_at']))+'.json');p.write_text(json.dumps(out,indent=2))
print(json.dumps(out))
