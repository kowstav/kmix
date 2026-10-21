from pathlib import Path
import subprocess
import sys
import os
import json

W=Path('/kaggle/working/hp_round11')
assert not (W/'warm_mixer_v1').exists(), 'Inspect existing registered replay job rather than duplicate'
env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
log=(W/'warm_mixer_launch.log').open('xb')
p=subprocess.Popen([sys.executable,str(W/'warm_mixer_worker.py')],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'status':'LONGER_WARM_MIXER_REPLAY_LAUNCHED_ONCE','new_native_observers':0,'GPU':False}))
