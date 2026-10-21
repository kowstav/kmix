from pathlib import Path
import json
import os
import py_compile
import subprocess

W=Path('/kaggle/working/hp_round11')
assert json.loads((W/'preflight_v4/manifest.json').read_text())['status']=='COMPLETE_NATIVE_PREFLIGHT_PASS_SERIALIZED_VOCABULARY'
prior=json.loads((W/'private_cpu_submission_v2_manifest.json').read_text())
assert prior['jobs']==[] and prior['dataset_action']=='CREATED_PRIVATE'
assert prior['failed_gate']=='private dataset delivery could not be verified'
assert not (W/'private_cpu_submission_v3_manifest.json').exists()
source=W/'research_round10_private_cpu_submit_worker.py'
py_compile.compile(str(source),doraise=True)
env={**os.environ,'HP_DISPATCH_ROOT':str(W),'HP_DISPATCH_MANIFEST':'private_cpu_submission_v3_manifest.json'}
child=subprocess.Popen(['python3',str(source)],env=env,stdout=(W/'private_cpu_submission_v3.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':child.pid,'status':'POSITIONAL_DATASET_DOWNLOAD_FIX_DISPATCH_LAUNCHED_ONCE',
                 'reason':'installed CLI 2.0.2 rejects legacy -d; private dataset already exists and is reused after full verification','GPU':False}))
