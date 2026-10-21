from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');p=W/'guard_storage_build_v1.json'
if p.exists():print(p.read_text())
else:
    q=subprocess.Popen(['python3','/kaggle/working/research_round14_build_packed_guard_worker.py'],stdout=(W/'guard_storage_build_v1.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'pid':q.pid,'manifest':str(p)}))
