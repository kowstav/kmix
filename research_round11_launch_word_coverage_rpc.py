from pathlib import Path
import subprocess
import sys
import os
import json
import hashlib

W=Path('/kaggle/working/hp_round11')
assert not (W/'word_coverage_v1').exists(), 'Inspect existing census before launch'
source=W/'word_coverage_worker.py'
env={**os.environ,'PYTHONPATH':'/root/hp_round11_constructor_v1/code','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
log=(W/'word_coverage_launch.log').open('xb')
process=subprocess.Popen([sys.executable,str(source)],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':process.pid,'status':'WORD_APPEARANCE_CONSTRUCTOR_CENSUS_STARTED_ONCE',
                  'worker_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'GPU':False}))
