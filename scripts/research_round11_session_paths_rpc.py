from pathlib import Path
import json
import hashlib
import subprocess

W = Path('/kaggle/working')
(W / 'hp_round11').mkdir(exist_ok=True)
out = {'session': 355983921, 'root_scratch_present': Path('/root/hp_round10').exists(), 'paths': {}, 'preflight_logs': {}}
for name in ['hp_round8/native_stage_trace_v1/tree/cmix', 'hp_round7/lex_audit/lex_h1_run11.tfwc2',
             'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt', 'hp_round7/preserved/data/vocab.bm',
             'hp_round7/preserved/data/enwik9.zip', 'hp_round10/local_code_models.zip',
             'hp_round10/private_cpu_assets_manifest.json', 'hp_round10/private_cpu_submission_manifest.json']:
    path = W / name
    out['paths'][name] = {'exists': path.exists(), 'bytes': path.stat().st_size if path.is_file() else None}
    if path.is_file() and path.stat().st_size < 5000000:
        out['paths'][name]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
for name in ['encode.log', 'decode.log']:
    path = W / 'hp_round10/preflight_v3' / name
    if path.exists():
        out['preflight_logs'][name] = path.read_text(errors='replace')[-2500:]
print(json.dumps(out))
