from pathlib import Path
import json
import os
import py_compile
import subprocess

W=Path('/kaggle/working/hp_round11')
prior=json.loads((W/'private_cpu_submission_v3_manifest.json').read_text())
assert prior['jobs']==[] and prior['dataset_action']=='REUSED_EXISTING'
assert prior['failed_gate']=='unknown owned-list schema'
assert prior['delivered_assets_all_entry_SHA_verified'] is True
assert not (W/'private_cpu_submission_v4_manifest.json').exists()
source=W/'research_round10_private_cpu_submit_worker.py'
py_compile.compile(str(source),doraise=True)
env={**os.environ,'HP_DISPATCH_ROOT':str(W),'HP_DISPATCH_MANIFEST':'private_cpu_submission_v4_manifest.json'}
child=subprocess.Popen(['python3',str(source)],env=env,stdout=(W/'private_cpu_submission_v4.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':child.pid,'status':'OBSERVED_EMPTY_OWNER_INVENTORY_SCHEMA_FIX_LAUNCHED_ONCE',
                 'verified_gate':'prior downloaded private dataset matches every entry SHA', 'GPU':False}))
