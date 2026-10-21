from pathlib import Path
import json,subprocess
W=Path('/kaggle/working/hp_round13');p=W/'dispatch_v1.json'
if p.exists():print(json.dumps({'action':'REUSE','manifest':json.loads(p.read_text())}))
else:
    with (W/'dispatch_controller_v1.log').open('x') as f:
        process=subprocess.Popen(['python3',str(W/'dispatch_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'action':'LAUNCHED','pid':process.pid,'manifest':str(p)}))
