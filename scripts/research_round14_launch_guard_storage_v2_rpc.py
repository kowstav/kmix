from pathlib import Path
import subprocess,json,hashlib
W=Path('/kaggle/working/hp_round14');p=W/'guard_storage_build_v2.json'
assert hashlib.sha256((W/'probability_tables_packed_v2.inc.dat').read_bytes()).hexdigest()=='6eb41d6bd3c78ffdaa83854e374eb7ef4167e97f27b305c4debbd8308114e059'
if p.exists():print(p.read_text())
else:
    q=subprocess.Popen(['python3','/kaggle/working/research_round14_build_packed_guard_v2_worker.py'],stdout=(W/'guard_storage_build_v2.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'pid':q.pid,'manifest':str(p)}))
