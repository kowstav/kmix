"""Submit the frozen P4 development notebooks (v13, refs -v2); one verified receipt per job; never retry.

Run on Kaggle: python3 research_round14_dispatch_structx_v13.py.dat --jobs a,b
Verifies frozen source/kernels/protocol hashes, the passing live gate, the private asset dataset
receipt and manifest hash, private CPU metadata and the actual push URL. Stops at the first failure.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, time, traceback, zipfile

p = argparse.ArgumentParser(); p.add_argument('--jobs', required=True); args = p.parse_args()
tags = args.jobs.split(','); assert tags and all(t in ('a', 'b') for t in tags) and len(set(tags)) == len(tags)
W = Path('/kaggle/working/hp_round14')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


R = Path('/root/r14_structx_dispatch_' + time.strftime('%Y%m%d-%H%M%S', time.gmtime())); R.mkdir()
prep = json.loads((W / 'prepared_structx_v13.json.dat').read_text())
assert sha(W / 'sources_structx_v13.zip.dat') == prep['source_sha256']
assert sha(W / 'kernels_structx_v13.zip.dat') == prep['kernels_zip_sha256']
assert sha(W / 'research_round14_structx_freeze_v1.md.dat') == prep['protocol_sha256']
assert sha(W / 'research_round14_structx_freeze_v1_addendum_v13.md.dat') == prep['addendum_sha256']
rg = json.loads((W / 'p4_regate_v13.json').read_text()); assert rg['status'] == 'PASS_V13_READONLY_MOUNT_REGATE_IDENTICAL_HASHES' and rg['source_sha256'] == prep['source_sha256']
g = json.loads((W / 'p4_gate_v2.json').read_text()); assert g['status'] == 'PASS_P4_GATE_ALIGNMENT_FUZZ_AND_NATIVE_INVERSES'
assert g['assets']['manifest_sha256'] == prep['asset_manifest_sha256']
d = json.loads((W / 'structx_assets_dataset_v1.json').read_text())
assert d['status'] == 'COMPLETE_PRIVATE_DATASET_READY' and d['asset_manifest_sha256'] == prep['asset_manifest_sha256']
with zipfile.ZipFile(W / 'sources_structx_v13.zip.dat') as z:
    for e in json.loads(z.read('source_manifest.json')):
        q = (R / 'code' / e['path']).resolve(); assert q.is_relative_to(R); b = z.read(e['path'])
        assert hashlib.sha256(b).hexdigest() == e['sha256']; q.parent.mkdir(parents=True, exist_ok=True); q.write_bytes(b)
sys.path.insert(0, str(R / 'code')); from hutter_research.dispatch_contracts import parse_successful_push
with zipfile.ZipFile(W / 'kernels_structx_v13.zip.dat') as z:
    for name in z.namelist(): assert (R / name).resolve().is_relative_to(R)
    z.extractall(R)
for tag in tags:
    receipt = W / ('structx_development_' + tag + '_dispatch_v13.json')
    assert not receipt.exists(), 'receipt exists: inspect, do not duplicate'
    M = {'status': 'VERIFYING', 'job': tag, 'started': time.time(), 'deletions': [], 'GPU': False, 'paid_usd': 0}
    def save(): receipt.write_text(json.dumps(M, indent=2))
    try:
        save()
        job = next(j for j in prep['jobs'] if j['folder'].endswith('-' + tag + '-v2')); folder = R / job['folder']
        assert sha(folder / 'main.py') == job['main_sha256']
        meta = json.loads((folder / 'kernel-metadata.json').read_text())
        assert meta['id'] == job['ref'] and meta['title'] == job['folder'] and meta['is_private'] is True
        assert meta['enable_gpu'] is False and meta['enable_tpu'] is False and meta['enable_internet'] is False
        assert meta['dataset_sources'] == ['chaoscpp/hutter-r14-structx-assets-v1']
        q = subprocess.run(['kaggle', 'kernels', 'list', '--mine', '--search', job['folder'], '--csv'], capture_output=True, text=True, timeout=60)
        assert q.returncode == 0 and job['ref'] not in q.stdout, 'existing ref or lookup failure: inspect, do not duplicate'
        q = subprocess.run(['kaggle', 'kernels', 'push', '-p', str(folder)], capture_output=True, text=True, timeout=180)
        M['push_exit'] = q.returncode; verified = None
        try:
            verified = parse_successful_push(q.stdout, 'chaoscpp') if q.returncode == 0 else None
        except ValueError as e:
            M['push_rejection'] = str(e)
        if not verified:
            tail = (q.stdout + q.stderr)[-600:]
            M['push_output_tail'] = '\n'.join(l for l in tail.splitlines() if 'token' not in l.lower())
        assert verified and verified['actual_ref'] == job['ref'], 'unverified push: no automatic retry'
        M.update(status='COMPLETE_VERIFIED_PRIVATE_CPU_PUSH', job=job, verified_push=verified, finished=time.time()); save()
        print(json.dumps({'job': tag, 'status': M['status'], 'ref': verified['actual_ref'], 'version': verified['version']}))
    except BaseException as e:
        M.update(status='FAIL_PRESERVED_NO_RETRY', error=repr(e), traceback=traceback.format_exc(), finished=time.time()); save()
        print(json.dumps({'job': tag, 'status': M['status'], 'error': repr(e)})); raise
