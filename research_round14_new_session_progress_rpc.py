from pathlib import Path
import json, time, shutil, zipfile, hashlib
W=Path('/kaggle/working/hp_round14');out={'time':time.time(),'working_free':shutil.disk_usage(W).free}
names=['confirm_b_dispatch_v5.json','confirmation_collection_a-20261009-1734.json','confirmation_collection_combo-20261009-1734.json']
for name in names:
    p=W/name
    if p.exists():out[name]=json.loads(p.read_text())
    log=p.with_suffix('.log')
    if log.exists():out[name+'_log_tail']=log.read_text()[-2000:]
small=W/'live_gate_receipts_356823832_v1.zip'
if not small.exists():
    paths=['guard_storage_parity_v2/manifest.json','guard_storage_parity_v1/manifest.json','guard_storage_parity_v1/manifest_original_bad_scope_label.json','guard_match_pipeline_v1.json','guard_match_scope_gate_release_v2.json','guard_match_hold_for_scope_correction_v1.json','resume_356823832_v1.json']
    entries=[]
    with zipfile.ZipFile(small,'x',zipfile.ZIP_DEFLATED) as z:
        for name in paths:
            p=W/name;b=p.read_bytes();z.writestr(name,b);entries.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
        z.writestr('entries.json',json.dumps(entries,indent=2))
out['small_bundle']={'name':small.name,'sha256':hashlib.sha256(small.read_bytes()).hexdigest(),'bytes':small.stat().st_size}
print(json.dumps(out))
