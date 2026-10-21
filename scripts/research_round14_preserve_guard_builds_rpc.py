from pathlib import Path
import hashlib,json,zipfile,time
W=Path('/kaggle/working/hp_round14');p=W/'guard_storage_artifacts_v2.zip';rows=[]
if not p.exists():
    m=json.loads((W/'guard_storage_build_v2.json').read_text());assert m['status']=='COMPLETE_BUILDS_AWAITING_NATIVE_PARITY'
    with zipfile.ZipFile(p,'x',zipfile.ZIP_DEFLATED) as z:
        files=list((W/'guard_storage_binaries_v2').iterdir())+[W/'guard_storage_build_v2.json',W/'guard_storage_build_v1.json',W/'probability_tables_packed_v2.inc.dat',W/'compiler_restore_session356740330_v2.json']
        for q in sorted(files):
            b=q.read_bytes();name=q.relative_to(W).as_posix();z.writestr(name,b);rows.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
        z.writestr('entries.json',json.dumps(rows,indent=2))
    meta={'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'entries':len(rows),'time':time.time()};(W/'guard_storage_preservation_v2.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta))
else:print((W/'guard_storage_preservation_v2.json').read_text())
q=W/'guard_storage_parity_v1/manifest.json'
if q.exists():
    m=json.loads(q.read_text());print('parity',json.dumps({k:v for k,v in m.items() if k!='cases'}),'cases',len(m['cases']))
