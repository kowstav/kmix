from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round13')
assert not (W/'native_preflight_v1.json').exists(),'inspect prior preflight, no duplicate launch'
assert json.loads((W/'native_build_v1.json').read_text())['status']=='COMPLETE_LAB_BINARIES_AWAITING_PARITY_PREFLIGHT'
with (W/'native_preflight_worker.log').open('xb') as f:
    p=subprocess.Popen(['python',str(W/'native_preflight_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'manifest':str(W/'native_preflight_v1.json')}))
