"""Submit frozen P1 A/B/B/A timing notebooks; one verified receipt per arm.

Run on Kaggle: python3 research_round14_dispatch_timing_abba.py.dat --arms prune_word,prune_match
Verifies the frozen source/kernels/references/protocol hashes, the live 16 KiB gate,
both terminal component confirmation collections, private CPU metadata and the actual
push URL. Refuses an arm whose receipt exists or whose ref is already listed.
Stops at the first failure or rejection (e.g. concurrency limit); never retries.
"""

# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
import argparse, hashlib, json, subprocess, sys, time, traceback, zipfile

ARMS = ('prune_word', 'prune_match', 'prune_indirect', 'output_fp32')
p = argparse.ArgumentParser(); p.add_argument('--arms', required=True); args = p.parse_args()
arms = args.arms.split(','); assert arms and all(a in ARMS for a in arms) and len(set(arms)) == len(arms)
W = Path('/kaggle/working/hp_round14')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


stamp = time.strftime('%Y%m%d-%H%M%S', time.gmtime())
R = Path('/root/r14_timing_abba_dispatch_' + stamp); assert not R.exists(); R.mkdir()
prep = json.loads((W / 'prepared_timing_abba_v9.json.dat').read_text())
assert prep['source_sha256'] == 'c792a9fbb6151b0b7c9366517a21413c038188620ca65b6b4155e41b58cbba2c'
assert sha(W / 'sources_timing_abba_v9.zip.dat') == prep['source_sha256']
assert sha(W / 'kernels_timing_abba_v9.zip.dat') == prep['kernels_zip_sha256']
assert sha(W / 'timing_abba_references_v9.json.dat') == prep['references_sha256']
assert sha(W / 'research_round14_timing_abba_freeze_v1.md.dat') == prep['protocol_sha256']
gate = json.loads((W / 'timing_abba_preflight_v9b/summary.json').read_text())
assert gate['source_sha256'] == prep['source_sha256']
for a in arms:  # per-arm gate (freeze: "for neutral and the arm"), checked again from the arm's own manifest
    g = json.loads((W / 'timing_abba_preflight_v9b' / (a + '_manifest.json')).read_text())
    assert gate['arms'].get(a) == g['status'] == 'PASS_16KIB_PREFLIGHT_REFERENCE_PARITY', a
    assert g['preflight_16KiB'] is True and g['arm'] == a and g['all_reference_hashes_match'] is True and len(g['pairs']) == 4
for tag in ('a-20261009-1734', 'b-20261009-2328'):
    assert json.loads((W / ('confirmation_collection_' + tag + '.json')).read_text())['status'] == 'TERMINAL_WAVE_SNAPSHOT'
with zipfile.ZipFile(W / 'sources_timing_abba_v9.zip.dat') as z:
    for e in json.loads(z.read('source_manifest.json')):
        q = (R / 'code' / e['path']).resolve(); assert q.is_relative_to(R); b = z.read(e['path'])
        assert hashlib.sha256(b).hexdigest() == e['sha256']; q.parent.mkdir(parents=True, exist_ok=True); q.write_bytes(b)
sys.path.insert(0, str(R / 'code')); from hutter_research.dispatch_contracts import parse_successful_push
with zipfile.ZipFile(W / 'kernels_timing_abba_v9.zip.dat') as z:
    for name in z.namelist(): assert (R / name).resolve().is_relative_to(R)
    z.extractall(R)
for arm in arms:
    receipt = W / ('timing_abba_' + arm + '_dispatch_v9.json')
    assert not receipt.exists(), 'receipt exists: inspect, do not duplicate'
    M = {'status': 'VERIFYING', 'arm': arm, 'started': time.time(), 'deletions': [], 'GPU': False, 'paid_usd': 0}
    def save(): receipt.write_text(json.dumps(M, indent=2))
    try:
        save()
        job = next(j for j in prep['jobs'] if j['arm'] == arm); folder = R / job['folder']
        assert sha(folder / 'main.py') == job['main_sha256']
        meta = json.loads((folder / 'kernel-metadata.json').read_text())
        assert meta['id'] == job['ref'] and meta['title'] == job['folder'] and meta['is_private'] is True
        assert meta['enable_gpu'] is False and meta['enable_tpu'] is False and meta['enable_internet'] is False
        assert meta['dataset_sources'] == ['chaoscpp/hutter-r13-four-lane-cpu-assets-v1', 'chaoscpp/hutter-r14-native-cpu-assets-v1']
        q = subprocess.run(['kaggle', 'kernels', 'list', '--mine', '--search', job['folder'], '--csv'], capture_output=True, text=True, timeout=60)
        assert q.returncode == 0 and job['ref'] not in q.stdout, 'existing ref or lookup failure: inspect, do not duplicate'
        q = subprocess.run(['kaggle', 'kernels', 'push', '-p', str(folder)], capture_output=True, text=True, timeout=180)
        M['push_exit'] = q.returncode
        verified = None
        try:
            verified = parse_successful_push(q.stdout, 'chaoscpp') if q.returncode == 0 else None
        except ValueError as e:
            M['push_rejection'] = str(e)
        if not verified:
            tail = (q.stdout + q.stderr)[-600:]
            M['push_output_tail'] = '\n'.join(l for l in tail.splitlines() if 'token' not in l.lower())
        assert verified and verified['actual_ref'] == job['ref'], 'unverified push: no automatic retry'
        M.update(status='COMPLETE_VERIFIED_PRIVATE_CPU_PUSH', job=job, verified_push=verified, finished=time.time()); save()
        print(json.dumps({'arm': arm, 'status': M['status'], 'ref': verified['actual_ref'], 'version': verified['version']}))
    except BaseException as e:
        M.update(status='FAIL_PRESERVED_NO_RETRY', error=repr(e), traceback=traceback.format_exc(), finished=time.time()); save()
        print(json.dumps({'arm': arm, 'status': M['status'], 'error': repr(e)}))
        raise
