"""Submit the frozen P5 template development-screen notebook (v11) once; never retry.

Run on Kaggle: python3 research_round14_dispatch_template.py.dat
Verifies frozen source/kernels/protocol hashes, the live real-data gate, private CPU
metadata and the actual push URL; refuses if the receipt exists or the ref is listed.
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
import hashlib, json, subprocess, sys, time, traceback, zipfile

W = Path('/kaggle/working/hp_round14')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


receipt = W / 'template_development_dispatch_v11.json'
assert not receipt.exists(), 'receipt exists: inspect, do not duplicate'
R = Path('/root/r14_template_dispatch_' + time.strftime('%Y%m%d-%H%M%S', time.gmtime())); R.mkdir()
M = {'status': 'VERIFYING', 'started': time.time(), 'deletions': [], 'GPU': False, 'paid_usd': 0}
def save(): receipt.write_text(json.dumps(M, indent=2))
try:
    save()
    prep = json.loads((W / 'prepared_template_v11.json.dat').read_text())
    assert prep['source_sha256'] == 'b80255f7b6965dfb79c6b76837613ebe8d3890aa5e3b508d68674c2eb0999374'
    assert sha(W / 'sources_template_v11.zip.dat') == prep['source_sha256']
    assert sha(W / 'kernels_template_v11.zip.dat') == prep['kernels_zip_sha256']
    assert sha(W / 'research_round14_template_freeze_v1.md.dat') == prep['protocol_sha256']
    gate = json.loads((W / 'template_preflight_v11/summary.json').read_text())
    assert gate['status'] == 'PASS_REAL_DATA_TEMPLATE_PREFLIGHT_INVERSES_AND_BASELINE_IDENTITY' and gate['source_sha256'] == prep['source_sha256']
    assert all(c['exact_inverse'] for c in gate['cases']) and sum(1 for c in gate['cases'] if c['constructor_codec_identity']) == 3
    with zipfile.ZipFile(W / 'sources_template_v11.zip.dat') as z:
        for e in json.loads(z.read('source_manifest.json')):
            q = (R / 'code' / e['path']).resolve(); assert q.is_relative_to(R); b = z.read(e['path'])
            assert hashlib.sha256(b).hexdigest() == e['sha256']; q.parent.mkdir(parents=True, exist_ok=True); q.write_bytes(b)
    sys.path.insert(0, str(R / 'code')); from hutter_research.dispatch_contracts import parse_successful_push
    with zipfile.ZipFile(W / 'kernels_template_v11.zip.dat') as z:
        for name in z.namelist(): assert (R / name).resolve().is_relative_to(R)
        z.extractall(R)
    job = prep['jobs'][0]; folder = R / job['folder']
    assert sha(folder / 'main.py') == job['main_sha256']
    meta = json.loads((folder / 'kernel-metadata.json').read_text())
    assert meta['id'] == job['ref'] and meta['title'] == job['folder'] and meta['is_private'] is True
    assert meta['enable_gpu'] is False and meta['enable_tpu'] is False and meta['enable_internet'] is False
    assert meta['dataset_sources'] == ['chaoscpp/hutter-r13-four-lane-cpu-assets-v1']
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
