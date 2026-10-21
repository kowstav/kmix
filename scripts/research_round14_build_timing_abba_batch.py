"""Freeze the four P1 A/B/B/A timing notebooks (one per component arm).

Writes, without overwriting anything: kaggle_cpu_round14/sources_timing_abba_v9.zip,
four notebook folders, kernels_timing_abba_v9.zip, prepared_timing_abba_v9.json and
timing_abba_references_v9.json (confirmation references for regions 8/9 and the
stored 16 KiB region-0 preflight references used by the live gate).
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
import ast, base64, hashlib, json, time, zipfile

R = project_root(__file__); O = project_path('kaggle_cpu_round14', base=R)
ARMS = ('prune_word', 'prune_match', 'prune_indirect', 'output_fp32')
KEYS = ('archive_sha256', 'probabilities_sha256', 'archive_bytes')


def h(b): return hashlib.sha256(b).hexdigest()


# References: region 8 from confirmation A, region 9 from confirmation B (identical binaries).
ref = {'8': {}, '9': {}}
for tag, region in (('a-20261009-1734', 8), ('b-20261009-2328', 9)):
    for p in (project_path('research_round14_confirmation_compact_' + tag + '_evidence', base=R)).rglob('manifest.json'):
        m = json.loads(p.read_text())
        for reg in m['regions']:
            if reg['region'] != region: continue
            for c in reg['cases']:
                row = {k: c[k] for k in KEYS} | {'binary_sha256': c['binary_sha256'], 'input_sha256': c['input_sha256']}
                assert ref[str(region)].setdefault(c['mode'], row) == row, 'reference differs across notebooks'
for region in ('8', '9'): assert set(ref[region]) == {'neutral', *ARMS}, ref[region].keys()
pre = json.loads((project_path('research_round14_native_cpu_evidence/preflight_manifest.json', base=R)).read_text())
ref0 = {}
for c in pre['cases']:
    if c['mode'] in ('neutral', *ARMS):
        assert c['region'] == 0 and c['bytes'] == 16384
        ref0[c['mode']] = {k: c[k] for k in KEYS} | {'binary_sha256': c['binary_sha256'], 'input_sha256': c['input_sha256']}
assert set(ref0) == {'neutral', *ARMS}
refs = {'confirmation_regions': ref, 'preflight_region0_16KiB': {'0': ref0},
        'sources': ['research_round14_confirmation_compact_a-20261009-1734 (region 8)',
                    'research_round14_confirmation_compact_b-20261009-2328 (region 9)',
                    'research_round14_native_cpu_evidence/preflight_manifest.json (16 KiB region 0)']}
rp = O / 'timing_abba_references_v9.json'; assert not rp.exists()
rp.write_text(json.dumps(refs, indent=2))

zp = O / 'sources_timing_abba_v9.zip'; assert not zp.exists(); entries = []
with zipfile.ZipFile(zp, 'x', zipfile.ZIP_DEFLATED) as z:
    for p in sorted((project_path('hutter_research', base=R)).rglob('*')):
        if not p.is_file() or p.suffix not in ('.py', '.cpp', '.h', '.hpp', '.inc') or '__pycache__' in p.parts: continue
        b = p.read_bytes(); n = p.relative_to(R).as_posix()
        if p.suffix == '.py': ast.parse(b.decode('utf-8'))
        z.writestr(n, b); entries.append({'path': n, 'bytes': len(b), 'sha256': h(b)})
    z.writestr('source_manifest.json', json.dumps(entries, indent=2))
assert any(e['path'] == 'hutter_research/cpu_round14_timing_abba.py' for e in entries)
blob = zp.read_bytes(); digest = h(blob); jobs = []
protocol = project_path('research_round14_timing_abba_freeze_v1.md', base=R)
for arm in ARMS:
    slug = 'hutter-r14-' + arm.replace('_', '-') + '-timing-abba-v1'; folder = O / slug; folder.mkdir()
    reference = {'8': {k: ref['8'][k] for k in ('neutral', arm)}, '9': {k: ref['9'][k] for k in ('neutral', arm)}}
    main = """import os,sys,zipfile,io,base64,hashlib,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
raw=base64.b64decode(__BLOB__);assert hashlib.sha256(raw).hexdigest()==__SHA__
root=Path('/root/r14_code_timing_abba_v9');root.mkdir()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for e in json.loads(z.read('source_manifest.json')):
        p=(root/e['path']).resolve();assert p.is_relative_to(root);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
sys.path.insert(0,str(root))
from hutter_research.cpu_round14_timing_abba import main
REFERENCE=json.loads(__REF__)
if __name__=='__main__':main(__ARM__,(8,9),REFERENCE)
""".replace('__BLOB__', repr(base64.b64encode(blob).decode())).replace('__SHA__', repr(digest)).replace(
        '__ARM__', repr(arm)).replace('__REF__', repr(json.dumps(reference, sort_keys=True)))
    ast.parse(main); (folder / 'main.py').write_bytes(main.encode())
    meta = {'id': 'chaoscpp/' + slug, 'title': slug, 'code_file': 'main.py', 'language': 'python', 'kernel_type': 'script',
            'is_private': True, 'enable_gpu': False, 'enable_tpu': False, 'enable_internet': False,
            'dataset_sources': ['chaoscpp/hutter-r13-four-lane-cpu-assets-v1', 'chaoscpp/hutter-r14-native-cpu-assets-v1'],
            'competition_sources': [], 'kernel_sources': []}
    (folder / 'kernel-metadata.json').write_text(json.dumps(meta, indent=2))
    jobs.append({'ref': meta['id'], 'folder': slug, 'main_sha256': h(main.encode()), 'workers': 4, 'arm': arm,
                 'region_ids': [8, 9], 'lane_tasks': [[8, 'AB'], [8, 'BA'], [9, 'AB'], [9, 'BA']]})
kz = O / 'kernels_timing_abba_v9.zip'; assert not kz.exists()
with zipfile.ZipFile(kz, 'x', zipfile.ZIP_DEFLATED) as z:
    for j in jobs:
        for p in sorted((O / j['folder']).iterdir()): z.write(p, p.relative_to(O).as_posix())
prep = {'frozen': time.time(), 'jobs': jobs, 'source_sha256': digest, 'protocol_sha256': h(protocol.read_bytes()),
        'references_sha256': h(rp.read_bytes()), 'kernels_zip_sha256': h(kz.read_bytes()),
        'binary_unchanged': True, 'gpu': False, 'workers_per_job': 4, 'deadline_hours': 10.3}
pp = O / 'prepared_timing_abba_v9.json'; assert not pp.exists()
pp.write_text(json.dumps(prep, indent=2)); print(json.dumps(prep, indent=2))
