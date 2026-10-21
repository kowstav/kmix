"""Independent PPMd-H implementation gate on all three preserved real failures."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib,json,os,subprocess,time,traceback,zipfile,resource
R=Path('/root/r14_ppmd_native_probe');SRC=Path('/root/r14_backend_probe')
W=Path('/kaggle/working/hp_round14');M={'status':'STARTING','started':time.time(),'cases':[],'workers':4,'deletions':[]}
def sha(b):return hashlib.sha256(b).hexdigest()
def case(i,order,rev):
    root=R/f'{i}_{order}_{rev}';root.mkdir();src=SRC/f'region_{i}_{order}_{rev}.raw';raw=src.read_bytes()
    dst=root/'archive.7z';cmd=['7z','a','-t7z','-m0=PPMd:mem=64m:o='+str(order),'-mmt=1','-mtm=off','-mtc=off','-mta=off','-bd','-bb0','-y','-sistored.bin',str(dst)]
    before=resource.getrusage(resource.RUSAGE_CHILDREN);started=time.time()
    p=subprocess.run(cmd,input=raw,capture_output=True,timeout=120);assert p.returncode==0,p.stderr
    q=subprocess.run(['7z','x','-so','-bd',str(dst)],capture_output=True,timeout=120);assert q.returncode==0,q.stderr
    assert q.stdout==raw,('native inverse mismatch',i,order)
    r=subprocess.run(['7z','l','-slt',str(dst)],capture_output=True,text=True,timeout=15)
    assert r.returncode==0 and 'PPMd' in r.stdout
    (root/'method.txt').write_text(r.stdout)
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    return {'region':i,'order':order,'reverse':rev,'raw_bytes':len(raw),'raw_sha256':sha(raw),'archive_bytes':dst.stat().st_size,'archive_sha256':sha(dst.read_bytes()),'exact':True,'CPU_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'wall_seconds':time.time()-started}
def save():(W/'ppmd_native_probe_v1.json').write_text(json.dumps(M,indent=2))
try:
    assert not R.exists();R.mkdir();M['tool_version']=subprocess.run(['7z'],capture_output=True,text=True).stdout[:650];save()
    with ProcessPoolExecutor(4) as p:
        for f in as_completed([p.submit(case,*v) for v in [(0,8,False),(2,16,True),(3,8,False),(0,16,False)]]):M['cases'].append(f.result());save()
    M.update(status='PASS_FOUR_NATIVE_PPMDH_REAL_DATA_INVERSES',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_NATIVE_BACKEND_PRESERVED',error=repr(e),traceback=traceback.format_exc());save()
finally:
    # Preserve the three failing raw inputs and both failed/passing streams.
    zpath=W/'ppmd_real_failure_evidence_v1.zip';entries=[]
    if not zpath.exists():
        with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED) as z:
            candidates=list(SRC.glob('*.raw'))+list(SRC.glob('*.ppmd'))+list(R.rglob('*.7z'))+list(R.rglob('method.txt'))
            for p in sorted(candidates):
                name=('pyppmd/' if p.parent==SRC else 'native/')+(p.name if p.parent==SRC else str(p.relative_to(R)))
                b=p.read_bytes();z.writestr(name,b);entries.append({'path':name,'bytes':len(b),'sha256':sha(b)})
            for name in ('ppmd_backend_probe_v2.json','ppmd_h_probe_v1.json','ppmd_native_probe_v1.json'):
                b=(W/name).read_bytes();z.writestr(name,b);entries.append({'path':name,'bytes':len(b),'sha256':sha(b)})
            z.writestr('entries.json',json.dumps(entries,indent=2))
        M['preserved']={'path':str(zpath),'bytes':zpath.stat().st_size,'sha256':sha(zpath.read_bytes()),'entries':len(entries)};save()
