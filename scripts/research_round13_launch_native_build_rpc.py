from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round13')
assert not (W/'native_build_v1.json').exists(),'inspect existing build; no duplicate launch'
with (W/'native_build_worker.log').open('xb') as f:
    p=subprocess.Popen(['python',str(W/'build_native_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'launched_pid':p.pid,'manifest':str(W/'native_build_v1.json')}))
