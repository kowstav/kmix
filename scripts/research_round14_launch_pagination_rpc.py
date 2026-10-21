from pathlib import Path
import subprocess,json,os
W=Path('/kaggle/working/hp_round14');log=(W/'paginated_pull_v2.log').open('ab')
assert not (W/'paginated_collection_v2.json').exists()
p=subprocess.Popen(['python3','/kaggle/working/research_round14_paginated_pull_worker.py'],stdout=log,stderr=log,start_new_session=True,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
print(json.dumps({'pid':p.pid,'action':'recover_missing_output_pages_without_relaunch'}))
