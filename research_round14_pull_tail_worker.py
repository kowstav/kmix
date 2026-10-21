from pathlib import Path
import subprocess,json,time,traceback,hashlib,zipfile
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_batch_outputs');M={'started':time.time(),'status':'PULLING','jobs':[]}
def save():(W/'tail_collection_v1.json').write_text(json.dumps(M,indent=2))
try:
    assert not (W/'tail_collection_v1.json').exists();save()
    for slug in ('native-confirmation-a','article-order-ppmd'):
        ref='chaoscpp/hutter-r14-'+slug+'-v1';d=R/ref.split('/')[1];assert not d.exists();d.mkdir()
        p=subprocess.run(['kaggle','kernels','output',ref,'-p',str(d)],capture_output=True,text=True,timeout=900)
        M['jobs'].append({'ref':ref,'exit':p.returncode,'message':(p.stdout+p.stderr)[-2000:]});save();assert p.returncode==0
    entries=[];p=W/'tail_compact_v1.zip'
    with zipfile.ZipFile(p,'x',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for slug in ('native-confirmation-a','article-order-ppmd'):
            d=R/('hutter-r14-'+slug+'-v1')
            for f in d.rglob('*'):
                if f.is_file() and f.suffix in ('.json','.log','.cmx','.hpor'):
                    n=str(f.relative_to(R));z.write(f,n);entries.append({'path':n,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
        z.writestr('entries.json',json.dumps(entries,indent=2))
    M.update(status='COMPLETE',finished=time.time(),compact={'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'entries':len(entries)});save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
