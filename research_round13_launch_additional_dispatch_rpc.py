from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round13');assert not (W/'additional_dispatch_v1.json').exists()
with (W/'additional_dispatch_worker.log').open('xb') as f:
    p=subprocess.Popen(['python',str(W/'dispatch_additional_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'manifest':str(W/'additional_dispatch_v1.json')}))
