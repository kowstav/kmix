from pathlib import Path
import zipfile
import json
import hashlib
import subprocess
import sys

W=Path('/kaggle/working/hp_round11')
S=Path('/root/hp_round11_codec_v1')
assert not S.exists() and not (W/'weight_codec_v1').exists(), 'Inspect existing sweep rather than relaunch'
with zipfile.ZipFile(W/'weight_codec_sources.zip') as archive:
    rows=json.loads(archive.read('source_manifest.json'))
    S.mkdir()
    for name,row in rows.items():
        raw=archive.read(name)
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
        path=S/name; assert path.resolve().is_relative_to(S.resolve())
        path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
    (S/'source_manifest.json').write_text(json.dumps(rows,indent=2))
log=(W/'weight_codec_launch.log').open('wb')
process=subprocess.Popen([sys.executable,str(S/'worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':process.pid,'GPU':False,'status':'EXACT_CODEC_SWEEP_LAUNCHED_ONCE','source_entries_SHA_verified':True}))
