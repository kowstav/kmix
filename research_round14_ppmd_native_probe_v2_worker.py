"""Explicit input paths: the model order must not determine an input filename."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib,json,subprocess,time,traceback,resource
R=Path('/root/r14_ppmd_native_probe_v2');SRC=Path('/root/r14_backend_probe');W=Path('/kaggle/working/hp_round14')
M={'status':'STARTING','started':time.time(),'cases':[],'workers':4,'deletions':[],'repair':'v1 fourth case derived nonexistent raw filename from a new model order; explicit paths validated before launch'}
CASES=[('region_0_8_False.raw',8),('region_2_16_True.raw',16),('region_3_8_False.raw',8),('region_0_8_False.raw',16)]
def sha(b):return hashlib.sha256(b).hexdigest()
def case(i,name,order):
    root=R/str(i);root.mkdir();raw=(SRC/name).read_bytes();dst=root/'archive.7z'
    cmd=['7z','a','-t7z','-m0=PPMd:mem=64m:o='+str(order),'-mmt=1','-mtm=off','-mtc=off','-mta=off','-bd','-bb0','-y','-sistored.bin',str(dst)]
    before=resource.getrusage(resource.RUSAGE_CHILDREN);started=time.time()
    p=subprocess.run(cmd,input=raw,capture_output=True,timeout=120);assert p.returncode==0,p.stderr
    q=subprocess.run(['7z','x','-so','-bd',str(dst)],capture_output=True,timeout=120);assert q.returncode==0,q.stderr
    assert q.stdout==raw,('native inverse mismatch',name,order)
    r=subprocess.run(['7z','l','-slt',str(dst)],capture_output=True,text=True,timeout=15);assert r.returncode==0 and 'PPMd' in r.stdout
    (root/'method.txt').write_text(r.stdout);after=resource.getrusage(resource.RUSAGE_CHILDREN)
    return {'input':name,'order':order,'raw_bytes':len(raw),'raw_sha256':sha(raw),'archive_bytes':dst.stat().st_size,'archive_sha256':sha(dst.read_bytes()),'exact':True,'CPU_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'wall_seconds':time.time()-started}
def save():(W/'ppmd_native_probe_v2.json').write_text(json.dumps(M,indent=2))
try:
    assert not R.exists();R.mkdir()
    for name,order in CASES:assert (SRC/name).is_file()
    save()
    with ProcessPoolExecutor(4) as p:
        for f in as_completed([p.submit(case,i,*v) for i,v in enumerate(CASES)]):M['cases'].append(f.result());save()
    M.update(status='PASS_FOUR_NATIVE_PPMDH_REAL_DATA_INVERSES',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_NATIVE_BACKEND_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
