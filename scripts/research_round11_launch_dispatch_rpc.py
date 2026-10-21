from pathlib import Path
import json
import py_compile
import subprocess

W = Path('/kaggle/working')
preflight = json.loads((W/'hp_round11/preflight_v4/manifest.json').read_text())
assert preflight['status'] == 'COMPLETE_NATIVE_PREFLIGHT_PASS_SERIALIZED_VOCABULARY'
assets = json.loads((W/'hp_round11/private_cpu_assets_manifest.json').read_text())
assert assets['status'] == 'COMPLETE_PRIVATE_CPU_ASSETS_PREPARED_NOT_UPLOADED'
assert not (W/'hp_round11/private_cpu_submission_manifest.json').exists()
source = W/'hp_round11/research_round10_private_cpu_submit_worker.py'
py_compile.compile(str(source), doraise=True)
import os
child = subprocess.Popen(['python3', str(source)], env={**os.environ,'HP_DISPATCH_ROOT':str(W/'hp_round11')}, stdout=(W/'hp_round11/private_cpu_submission.log').open('x'),
                         stderr=subprocess.STDOUT, start_new_session=True)
print(json.dumps({'pid':child.pid,'status':'DISPATCH_STARTED_ONCE','GPU':False,'dataset': 'chaoscpp/hutter-round10-private-cpu-assets-v1'}))
