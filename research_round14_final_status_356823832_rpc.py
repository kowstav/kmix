from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,time,shutil
W=Path('/kaggle/working/hp_round14');p=W/'guard_match_confirm_a_dispatch_v8.json'
out={'time':time.time(),'joint_submission':json.loads(p.read_text()) if p.exists() else None,'working_free_B':shutil.disk_usage(W).free}
refs=['chaoscpp/hutter-r14-'+a+'-confirm-b-v1' for a in ('prune-word','prune-match','prune-indirect','output-fp32')]+['chaoscpp/hutter-r14-guard-match-confirm-a-v1']
def status(ref):
    q=subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=25)
    return {'ref':ref,'exit':q.returncode,'status':next((s for s in ('COMPLETE','RUNNING','QUEUED','ERROR') if 'KernelWorkerStatus.'+s in q.stdout),'UNKNOWN')}
with ThreadPoolExecutor(4) as pool:out['notebooks']=list(pool.map(status,refs))
(W/'session356823832_status_v1.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
