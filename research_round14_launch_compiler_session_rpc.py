from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');p=W/'compiler_restore_session356740330_v2.json'
if p.exists():print(p.read_text())
else:
    q=subprocess.Popen(['python3','/kaggle/working/research_round14_restore_compiler_session_worker.py'],stdout=(W/'compiler_restore_session356740330_v2.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'pid':q.pid,'manifest':str(p)}))
