from pathlib import Path
import json
import py_compile
import subprocess
import hashlib

W=Path('/kaggle/working/hp_round11')
assert not Path('/root/hp_round11_private_assets_v2').exists()
source=W/'research_round11_private_cpu_prepare_worker.py'
py_compile.compile(str(source),doraise=True)
child=subprocess.Popen(['python3',str(source)],stdout=(W/'private_cpu_assets_v2.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':child.pid,'status':'VERSIONED_ASSET_REPAIR_LAUNCHED_ONCE','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'GPU':False}))
