from pathlib import Path
import json,subprocess
W=Path('/kaggle/working/hp_round13');p=W/'compiler_restore_v1.json'
if p.exists():print(json.dumps({'action':'REUSE','manifest':json.loads(p.read_text())}))
else:
    with (W/'compiler_controller_v1.log').open('x') as f:
        child=subprocess.Popen(['python3',str(W/'restore_compiler_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'action':'LAUNCHED','pid':child.pid}))
