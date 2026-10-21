from pathlib import Path
import hashlib
import json
import zipfile
import subprocess
import sys
import os

W=Path('/kaggle/working/hp_round11')
S=Path('/root/hp_round11_constructor_v1')
assert not S.exists() and not (W/'constructor_proxy_v1').exists(), 'Inspect existing experiment before any launch'
with zipfile.ZipFile(W/'constructor_sources.zip') as archive:
    rows=json.loads(archive.read('source_manifest.json')); S.mkdir()
    for name,row in rows.items():
        raw=archive.read(name); assert hashlib.sha256(raw).hexdigest()==row['sha256'] and len(raw)==row['bytes']
        path=S/name; assert path.resolve().is_relative_to(S.resolve())
        path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
    (S/'source_manifest.json').write_text(json.dumps(rows,indent=2))
env={**os.environ,'PYTHONPATH':str(S/'code'),'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
log=(W/'constructor_launch.log').open('wb')
p=subprocess.Popen([sys.executable,str(S/'worker.py')],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'status':'PAID_CONSTRUCTOR_CPU_PROXY_LAUNCHED_ONCE','GPU':False,'verified_sources':True}))
