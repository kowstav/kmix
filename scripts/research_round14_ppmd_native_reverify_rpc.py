from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,subprocess,time
R=Path('/root/r14_ppmd_native_probe_v2');SRC=Path('/root/r14_backend_probe');W=Path('/kaggle/working/hp_round14')
CASES=[('region_0_8_False.raw',8),('region_2_16_True.raw',16),('region_3_8_False.raw',8),('region_0_8_False.raw',16)]
def verify(v):
    i,(name,order)=v;p=R/str(i)/'archive.7z';raw=(SRC/name).read_bytes()
    q=subprocess.run(['7z','x','-so','-bd',str(p)],capture_output=True,timeout=90);assert q.returncode==0 and q.stdout==raw
    r=subprocess.run(['7z','l','-slt',str(p)],capture_output=True,text=True,timeout=10)
    assert r.returncode==0 and 'Method = PPMD:o'+str(order)+':mem26' in r.stdout
    return {'input':name,'order':order,'raw_bytes':len(raw),'archive_bytes':p.stat().st_size,'raw_sha256':hashlib.sha256(raw).hexdigest(),'archive_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'exact':True,'method':'PPMD:o'+str(order)+':mem26'}
with ThreadPoolExecutor(4) as pool:rows=list(pool.map(verify,enumerate(CASES)))
m={'status':'PASS_FOUR_NATIVE_PPMDH_REAL_DATA_INVERSES','time':time.time(),'cases':rows,'source':'independently re-decode all four v2 streams, preserve v1 path and v2 case-sensitive method-check failures','deletions':[]}
(W/'ppmd_native_probe_v3.json').write_text(json.dumps(m,indent=2));print(json.dumps(m))
