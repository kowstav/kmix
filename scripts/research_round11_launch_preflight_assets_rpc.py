from pathlib import Path
import hashlib
import json
import subprocess
import py_compile

W = Path('/kaggle/working')
D = W / 'hp_round11'
D.mkdir(exist_ok=True)
out = []
for label, path, guard in [
    ('preflight_v4', D/'research_round11_preflight_worker.py', D/'preflight_v4'),
    ('private_cpu_assets', W/'hp_round10/research_round10_private_cpu_prepare_worker.py', Path('/root/hp_round10_private_assets_v1'))]:
    assert not guard.exists(), 'Inspect existing worker before launching: ' + str(guard)
    py_compile.compile(str(path), doraise=True)
    child = subprocess.Popen(['python3', str(path)], stdout=(D/(label+'.log')).open('x'),
                             stderr=subprocess.STDOUT, start_new_session=True)
    out.append({'label':label, 'pid':child.pid, 'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'GPU':False})
(D/'launch_manifest.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out))
