from pathlib import Path
import json
import os
import py_compile
import subprocess

W=Path('/kaggle/working/hp_round11')
assert json.loads((W/'preflight_v4/manifest.json').read_text())['status']=='COMPLETE_NATIVE_PREFLIGHT_PASS_SERIALIZED_VOCABULARY'
assert json.loads((W/'private_cpu_assets_manifest.json').read_text())['status']=='COMPLETE_PRIVATE_CPU_ASSETS_PREPARED_NOT_UPLOADED'
prior=json.loads((W/'private_cpu_submission_manifest.json').read_text())
assert prior['jobs']==[] and 'dataset_action' not in prior
assert prior['error_type']=='AssertionError'
assert not (W/'private_cpu_submission_v2_manifest.json').exists()
source=W/'research_round10_private_cpu_submit_worker.py'
py_compile.compile(str(source),doraise=True)
env={**os.environ,'HP_DISPATCH_ROOT':str(W),'HP_DISPATCH_MANIFEST':'private_cpu_submission_v2_manifest.json'}
child=subprocess.Popen(['python3',str(source)],env=env,stdout=(W/'private_cpu_submission_v2.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':child.pid,'status':'CORRECTED_OWNER_INVENTORY_DISPATCH_LAUNCHED_ONCE','reason':'absent-ref status was 403; first dispatch made no write and launched zero kernels','GPU':False}))
