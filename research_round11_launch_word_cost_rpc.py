from pathlib import Path
import subprocess
import sys
import os
import json

W=Path('/kaggle/working/hp_round11')
assert not (W/'word_cost_v1').exists(), 'Inspect existing word alignment before launch'
env={**os.environ,'PYTHONPATH':'/root/hp_round11_constructor_v1/code','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
log=(W/'word_cost_launch.log').open('xb')
p=subprocess.Popen([sys.executable,str(W/'word_cost_worker.py')],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'status':'EXACT_WORD_ALIGNMENT_CPU_JOB_LAUNCHED_ONCE','GPU':False}))
