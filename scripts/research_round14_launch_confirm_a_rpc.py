from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');p=W/'confirm_a_dispatch_v5.json'
if p.exists():print(p.read_text())
else:
    q=subprocess.Popen(['python3','/kaggle/working/research_round14_dispatch_confirmation_worker.py','--role','a'],stdout=(W/'confirm_a_dispatch_v5.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'pid':q.pid,'manifest':str(p)}))
