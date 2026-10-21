"""Submit the frozen joint G-vs-GM A/B/B/A timing notebook (v10) once; never retry.

Run on Kaggle: python3 research_round14_dispatch_timing_abba_joint.py.dat
Verifies frozen source/kernels/references/protocol hashes, the live 16 KiB gate for both
binaries, both terminal joint confirmation collections, private CPU metadata and the actual
push URL. Refuses if the receipt exists or the ref is already listed. Stops on failure.
"""
from pathlib import Path
import hashlib, json, subprocess, sys, time, traceback, zipfile

W = Path('/kaggle/working/hp_round14')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


receipt = W / 'timing_abba_guard_vs_guard_match_dispatch_v10.json'
assert not receipt.exists(), 'receipt exists: inspect, do not duplicate'
R = Path('/root/r14_timing_abba_joint_dispatch_' + time.strftime('%Y%m%d-%H%M%S', time.gmtime())); R.mkdir()
M = {'status': 'VERIFYING', 'started': time.time(), 'deletions': [], 'GPU': False, 'paid_usd': 0}
def save(): receipt.write_text(json.dumps(M, indent=2))
try:
    save()
    prep = json.loads((W / 'prepared_timing_abba_v10.json.dat').read_text())
    assert prep['source_sha256'] == '8951a4d60ad4fa55660c32ef6186fa21cc02387df710517a00d95732da4f3891'
    assert sha(W / 'sources_timing_abba_v10.zip.dat') == prep['source_sha256']
    assert sha(W / 'kernels_timing_abba_v10.zip.dat') == prep['kernels_zip_sha256']
    assert sha(W / 'timing_abba_references_v10.json.dat') == prep['references_sha256']
    assert sha(W / 'research_round14_timing_abba_joint_freeze_v1.md.dat') == prep['protocol_sha256']
    gate = json.loads((W / 'timing_abba_joint_preflight_v10/manifest.json').read_text())
    assert gate['status'] == 'PASS_16KIB_PREFLIGHT_REFERENCE_PARITY' and gate['preflight_16KiB'] is True
    assert gate['pair_label'] == 'guard_vs_guard_match' and gate['all_reference_hashes_match'] is True and len(gate['pairs']) == 4
    assert json.loads((W / 'timing_abba_joint_preflight_v10/summary.json').read_text())['source_sha256'] == prep['source_sha256']
    for tag in ('joint-a-20261009-2325', 'joint-b-20261010-0446'):
        assert json.loads((W / ('confirmation_collection_' + tag + '.json')).read_text())['status'] == 'TERMINAL_WAVE_SNAPSHOT'
    with zipfile.ZipFile(W / 'sources_timing_abba_v10.zip.dat') as z:
        for e in json.loads(z.read('source_manifest.json')):
            q = (R / 'code' / e['path']).resolve(); assert q.is_relative_to(R); b = z.read(e['path'])
            assert hashlib.sha256(b).hexdigest() == e['sha256']; q.parent.mkdir(parents=True, exist_ok=True); q.write_bytes(b)
    sys.path.insert(0, str(R / 'code')); from hutter_research.dispatch_contracts import parse_successful_push
    with zipfile.ZipFile(W / 'kernels_timing_abba_v10.zip.dat') as z:
        for name in z.namelist(): assert (R / name).resolve().is_relative_to(R)
        z.extractall(R)
    job = prep['jobs'][0]; folder = R / job['folder']
    assert sha(folder / 'main.py') == job['main_sha256']
    meta = json.loads((folder / 'kernel-metadata.json').read_text())
    assert meta['id'] == job['ref'] and meta['title'] == job['folder'] and meta['is_private'] is True
    assert meta['enable_gpu'] is False and meta['enable_tpu'] is False and meta['enable_internet'] is False
    assert meta['dataset_sources'] == ['chaoscpp/hutter-r13-four-lane-cpu-assets-v1', 'chaoscpp/hutter-r14-guard-match-assets-v1']
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
    print(json.dumps({'status': M['status'], 'ref': verified['actual_ref'], 'version': verified['version']}))
except BaseException as e:
    M.update(status='FAIL_PRESERVED_NO_RETRY', error=repr(e), traceback=traceback.format_exc(), finished=time.time()); save()
    print(json.dumps({'status': M['status'], 'error': repr(e)})); raise
