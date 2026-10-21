from pathlib import Path
import json
import subprocess
import py_compile
import hashlib

W=Path('/kaggle/working/hp_round11')
assert json.loads((W/'preflight_v4/manifest.json').read_text())['status']=='COMPLETE_NATIVE_PREFLIGHT_PASS_SERIALIZED_VOCABULARY'
assert not (W/'warm_atlas_v2').exists()
source=W/'research_round11_warm_atlas_worker.py'
py_compile.compile(str(source),doraise=True)
child=subprocess.Popen(['python3',str(source)],stdout=(W/'warm_atlas_v2.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':child.pid,'status':'WARM_NATIVE_ATLAS_LAUNCHED_ONCE','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'GPU':False}))
