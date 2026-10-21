from pathlib import Path
import os,signal,json,time,hashlib
W=Path('/kaggle/working/hp_round14');pid=587;cmd=Path(f'/proc/{pid}/cmdline')
row={'time':time.time(),'pid':pid,'reason':'archive_case preflight=True truncates to 16384; v1 storage manifest incorrectly claimed 64K. Hold orchestrator before private submission until actual 64K parity.'}
pipeline=json.loads((W/'guard_match_pipeline_v1.json').read_text());row['pipeline_status_before']=pipeline['status']
if cmd.exists():
    args=cmd.read_bytes().split(b'\x00');assert b'/kaggle/working/research_round14_guard_match_pipeline_worker.py' in args
    os.kill(pid,signal.SIGSTOP);row['action']='SIGSTOP_OWN_PIPELINE_PARENT_CHILD_PREFLIGHT_CAN_FINISH'
else:row['action']='PARENT_ALREADY_EXITED_INSPECT_RECEIPT'
p=W/'guard_storage_parity_v1/manifest.json';raw=p.read_bytes();m=json.loads(raw);assert all(r['bytes']==16384 for r in m['cases'])
backup=p.with_name('manifest_original_bad_scope_label.json');assert not backup.exists();backup.write_bytes(raw)
m.update(status='PASS_16K_PARITY_ONLY_ORIGINAL_64K_LABEL_ERROR',scope_correction={'original_manifest_sha256':hashlib.sha256(raw).hexdigest(),'actual_case_bytes':16384,'required_guard_case_bytes':65536,'time':time.time()});p.write_text(json.dumps(m,indent=2))
(W/'guard_match_hold_for_scope_correction_v1.json').write_text(json.dumps(row,indent=2));print(json.dumps(row))
