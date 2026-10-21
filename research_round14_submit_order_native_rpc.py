from pathlib import Path
import hashlib,json,subprocess,zipfile,sys,time
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_order_native_dispatch');record=W/'order_native_submission_v4.json'
assert not record.exists() and not R.exists();R.mkdir()
j=json.loads((W/'prepared_order_native_v4.json').read_text());gate=json.loads((W/'order_native_gate_v4.json').read_text())
assert gate['status']=='PASS_NATIVE_ORDER_CONTAINER_AND_REAL_CASES' and gate['source_sha256']==j['source_sha256']
with zipfile.ZipFile(W/'kernel_order_native_v4.zip.dat') as z:
    for n in z.namelist():assert (R/n).resolve().is_relative_to(R)
    z.extractall(R)
folder=R/j['folder'];assert hashlib.sha256((folder/'main.py').read_bytes()).hexdigest()==j['main_sha256']
q=subprocess.run(['kaggle','kernels','list','--mine','--search',j['ref'].split('/')[1],'--csv'],capture_output=True,text=True,timeout=30)
assert q.returncode==0 and j['ref'] not in q.stdout,'already exists or lookup failed; inspect instead of duplicate'
sys.path.insert(0,'/root/r14_order_native_gate');from hutter_research.dispatch_contracts import parse_successful_push
p=subprocess.run(['kaggle','kernels','push','-p',str(folder)],capture_output=True,text=True,timeout=45)
row={**j,'time':time.time(),'exit':p.returncode,'verified_push':None,'status':'UNVERIFIED_PUSH_DO_NOT_REPEAT'}
try:row['verified_push']=parse_successful_push(p.stdout,'chaoscpp') if p.returncode==0 else None
except ValueError:pass
if row['verified_push']:row['status']='VERIFIED_PRIVATE_CPU_PUSH'
else:row['error']=(p.stdout+p.stderr)[-1600:]
record.write_text(json.dumps(row,indent=2));print(json.dumps(row));assert row['verified_push'],'API rejection; inspect, no automatic retry'
