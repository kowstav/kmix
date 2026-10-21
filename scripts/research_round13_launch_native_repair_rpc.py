from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round13');assert not (W/'native_delivery_repair_v2.json').exists()
with (W/'native_delivery_repair_worker.log').open('xb') as f:
    p=subprocess.Popen(['python',str(W/'native_delivery_repair_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'manifest':str(W/'native_delivery_repair_v2.json')}))
