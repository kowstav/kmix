"""Create the private P4 asset dataset from the passing live gate's assets (once; never retried).

Run on Kaggle: python3 research_round14_create_structx_assets.py.dat
Requires hp_round14/p4_gate_v2.json status PASS_P4_GATE_ALIGNMENT_FUZZ_AND_NATIVE_INVERSES and
re-verifies every listed asset hash before upload. Receipt: hp_round14/structx_assets_dataset_v1.json.
"""
from pathlib import Path
import hashlib, json, shutil, subprocess, time, traceback

W = Path('/kaggle/working/hp_round14'); receipt = W / 'structx_assets_dataset_v1.json'
DATASET = 'chaoscpp/hutter-r14-structx-assets-v1'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''): h.update(b)
    return h.hexdigest()


assert not receipt.exists(), 'receipt exists: inspect, do not duplicate'
M = {'status': 'VERIFYING', 'started': time.time(), 'dataset': DATASET, 'deletions': [], 'private': True}
def save(): receipt.write_text(json.dumps(M, indent=2))
try:
    save()
    g = json.loads((W / 'p4_gate_v2.json').read_text())
    assert g['status'] == 'PASS_P4_GATE_ALIGNMENT_FUZZ_AND_NATIVE_INVERSES'
    A = Path(g['assets']['dir']); meta = json.loads((A / 'structx_assets.json').read_text())
    assert sha(A / 'structx_assets.json') == g['assets']['manifest_sha256']
    for n, r in meta['files'].items(): assert (A / n).stat().st_size == r['bytes'] and sha(A / n) == r['sha256'], n
    up = Path('/root/r14_structx_dataset_upload'); assert not up.exists(); shutil.copytree(A, up)
    (up / 'dataset-metadata.json').write_text(json.dumps({'id': DATASET, 'title': 'hutter-r14-structx-assets-v1', 'licenses': [{'name': 'other'}]}))
    q = subprocess.run(['kaggle', 'datasets', 'list', '--mine', '--search', 'hutter-r14-structx-assets', '--csv'], capture_output=True, text=True, timeout=60)
    assert q.returncode == 0 and DATASET not in q.stdout, 'dataset exists or lookup failed: inspect, do not duplicate'
    q = subprocess.run(['kaggle', 'datasets', 'create', '-p', str(up)], capture_output=True, text=True, timeout=900)
    M['create_exit'] = q.returncode
    ok = q.returncode == 0 and ('https://www.kaggle.com/datasets/' + DATASET) in q.stdout and 'error' not in q.stdout.lower()
    M['create_output_tail'] = '\n'.join(l for l in (q.stdout + q.stderr).splitlines()[-6:] if 'token' not in l.lower())
    assert ok, 'private dataset result unverified; inspect, do not retry'
    M['status'] = 'CREATED_WAITING_FOR_FILES'; save()
    for _ in range(60):
        q = subprocess.run(['kaggle', 'datasets', 'files', DATASET, '--page-size', '50'], capture_output=True, text=True, timeout=120)
        if q.returncode == 0 and 'structx_assets.json' in q.stdout and all(n in q.stdout for n in meta['files']):
            break
        time.sleep(20)
    else:
        raise RuntimeError('dataset files not listed after 20 minutes')
    M.update(status='COMPLETE_PRIVATE_DATASET_READY', asset_manifest_sha256=sha(A / 'structx_assets.json'), files=len(meta['files']), finished=time.time()); save()
    print(json.dumps({'status': M['status'], 'dataset': DATASET}))
except BaseException as e:
    M.update(status='FAIL_PRESERVED_NO_RETRY', error=repr(e), traceback=traceback.format_exc()[-2000:], finished=time.time()); save(); raise
