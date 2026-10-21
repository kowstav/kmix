from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import os
import subprocess
import time

W = Path('/kaggle/working/hp_round11')
dispatch = json.loads((W/'private_cpu_submission_v4_manifest.json').read_text())
assert dispatch['status'] == 'COMPLETE_PRIVATE_CPU_SUBMISSION_DISPATCH'
assert os.environ.get('KAGGLE_API_TOKEN'), 'Credential absent; do not print or copy secrets'

def inspect(job):
    ref = job['id']
    result = subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=25)
    # Only the expected status line can enter the durable record.
    lines = [line.strip() for line in result.stdout.splitlines() if ref in line and 'status' in line.lower()]
    return {'ref':ref, 'exit':result.returncode, 'status_lines':lines, 'observed_at':time.time()}

with ThreadPoolExecutor(max_workers=3) as pool:
    rows = list(pool.map(inspect, dispatch['jobs']))
out = {'observed_at':time.time(), 'session':355983921, 'jobs':rows, 'deletions':[], 'paid_usd':0}
name = W / ('notebook_status_'+str(int(out['observed_at']))+'.json')
name.write_text(json.dumps(out,indent=2))
print(json.dumps({'record':str(name),'jobs':rows}))
