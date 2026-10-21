from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,time
W=Path('/kaggle/working/hp_round14');out={'observed_at':time.time()}
p=W/'preflight_v2.json'
if p.exists():
    m=json.loads(p.read_text());out['preflight']=m
    if m['status']=='COMPLETE_FOUR_LINUX_CORRECTNESS_TESTS' and not (W/'dispatch_v2.json').exists():
        child=subprocess.Popen(['python','/root/r14_dispatch_v2.py'],stdin=subprocess.DEVNULL,stdout=(W/'dispatch_v2.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
        out['dispatch_v2_launched']=child.pid
    elif m['status']=='FAIL_PRESERVED':
        out['install_log']=(W/'pyppmd_install.log').read_text(errors='replace')[-3500:]
        test=W/'preflight_tests_v2.log'
        if test.exists():out['test_log']=test.read_text(errors='replace')[-3500:]
refs=[]
for n in ('dispatch_v1.json','dispatch_v2.json'):
    if (W/n).exists():
        m=json.loads((W/n).read_text());out[n]={'status':m['status'],'error':m.get('error'),'jobs':m['jobs']}
        refs.extend(r['verified_push']['actual_ref'] for r in m['jobs'] if r.get('verified_push'))
def status(ref):
    p=subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=30)
    return {'ref':ref,'exit':p.returncode,'output':(p.stdout+p.stderr)[-1800:]}
with ThreadPoolExecutor(max_workers=6) as pool:out['jobs']=list(pool.map(status,refs))
print(json.dumps(out))
