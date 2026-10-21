"""Freeze the joint G-vs-GM A/B/B/A timing notebook (v10). Never overwrites anything.

Writes kaggle_cpu_round14/sources_timing_abba_v10.zip, the notebook folder
hutter-r14-guard-match-timing-abba-v1/, kernels_timing_abba_v10.zip,
timing_abba_references_v10.json and prepared_timing_abba_v10.json.
"""
from pathlib import Path
import ast, base64, hashlib, json, time, zipfile

R = Path(__file__).resolve().parent; O = R / 'kaggle_cpu_round14'
KEYS = ('archive_sha256', 'probabilities_sha256', 'archive_bytes')
MODES = ('guard_base', 'guard_match')


def h(b): return hashlib.sha256(b).hexdigest()


ref = {'8': {}, '9': {}}
for tag, region in (('joint-a-20261009-2325', 8), ('joint-b-20261010-0446', 9)):
    ps = list((R / ('research_round14_confirmation_compact_' + tag + '_evidence')).rglob('manifest.json')); assert len(ps) == 1
    for reg in json.loads(ps[0].read_text())['regions']:
        if reg['region'] == region:
            for c in reg['cases']:
                ref[str(region)][c['mode']] = {k: c[k] for k in KEYS} | {'binary_sha256': c['binary_sha256'], 'input_sha256': c['input_sha256']}
for region in ('8', '9'): assert set(ref[region]) == set(MODES)
pipe = json.loads((R / 'research_round14_live_gate_receipts_356823832_v1_evidence/guard_match_pipeline_v1.json').read_text())
ref0 = {}
for c in pipe['cases']:
    if c['region'] == 0 and c['bytes'] == 16384:
        ref0[c['mode']] = {k: c[k] for k in KEYS} | {'binary_sha256': c['binary_sha256'], 'input_sha256': c['input_sha256']}
assert set(ref0) == set(MODES)
assert ref0['guard_base']['input_sha256'].startswith('87ad632aad99fddd')
refs = {'confirmation_regions': ref, 'preflight_region0_16KiB': {'0': ref0},
        'sources': ['research_round14_confirmation_compact_joint-a-20261009-2325 (region 8)',
                    'research_round14_confirmation_compact_joint-b-20261010-0446 (region 9)',
                    'guard_match_pipeline_v1.json preflight cases (16 KiB, canonical region 0)']}
rp = O / 'timing_abba_references_v10.json'; assert not rp.exists(); rp.write_text(json.dumps(refs, indent=2))

zp = O / 'sources_timing_abba_v10.zip'; assert not zp.exists(); entries = []
with zipfile.ZipFile(zp, 'x', zipfile.ZIP_DEFLATED) as z:
    for p in sorted((R / 'hutter_research').rglob('*')):
        if not p.is_file() or p.suffix not in ('.py', '.cpp', '.h', '.hpp', '.inc') or '__pycache__' in p.parts: continue
        b = p.read_bytes(); n = p.relative_to(R).as_posix()
        if p.suffix == '.py': ast.parse(b.decode('utf-8'))
        z.writestr(n, b); entries.append({'path': n, 'bytes': len(b), 'sha256': h(b)})
    z.writestr('source_manifest.json', json.dumps(entries, indent=2))
assert any(e['path'] == 'hutter_research/cpu_round14_timing_abba_pair.py' for e in entries)
blob = zp.read_bytes(); digest = h(blob)
slug = 'hutter-r14-guard-match-timing-abba-v1'; folder = O / slug; folder.mkdir()
main = """import os,sys,zipfile,io,base64,hashlib,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
raw=base64.b64decode(__BLOB__);assert hashlib.sha256(raw).hexdigest()==__SHA__
root=Path('/root/r14_code_timing_abba_v10');root.mkdir()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for e in json.loads(z.read('source_manifest.json')):
        p=(root/e['path']).resolve();assert p.is_relative_to(root);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
sys.path.insert(0,str(root))
from hutter_research.cpu_round14_timing_abba_pair import main
REFERENCE=json.loads(__REF__)
if __name__=='__main__':main('guard_vs_guard_match',(8,9),REFERENCE)
""".replace('__BLOB__', repr(base64.b64encode(blob).decode())).replace('__SHA__', repr(digest)).replace(
    '__REF__', repr(json.dumps(ref, sort_keys=True)))
ast.parse(main); (folder / 'main.py').write_bytes(main.encode())
meta = {'id': 'chaoscpp/' + slug, 'title': slug, 'code_file': 'main.py', 'language': 'python', 'kernel_type': 'script',
        'is_private': True, 'enable_gpu': False, 'enable_tpu': False, 'enable_internet': False,
        'dataset_sources': ['chaoscpp/hutter-r13-four-lane-cpu-assets-v1', 'chaoscpp/hutter-r14-guard-match-assets-v1'],
        'competition_sources': [], 'kernel_sources': []}
(folder / 'kernel-metadata.json').write_text(json.dumps(meta, indent=2))
job = {'ref': meta['id'], 'folder': slug, 'main_sha256': h(main.encode()), 'workers': 4, 'pair_label': 'guard_vs_guard_match',
       'region_ids': [8, 9], 'lane_tasks': [[8, 'AB'], [8, 'BA'], [9, 'AB'], [9, 'BA']]}
kz = O / 'kernels_timing_abba_v10.zip'; assert not kz.exists()
with zipfile.ZipFile(kz, 'x', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(folder.iterdir()): z.write(p, p.relative_to(O).as_posix())
prep = {'frozen': time.time(), 'jobs': [job], 'source_sha256': digest,
        'protocol_sha256': h((R / 'research_round14_timing_abba_joint_freeze_v1.md').read_bytes()),
        'references_sha256': h(rp.read_bytes()), 'kernels_zip_sha256': h(kz.read_bytes()),
        'binary_unchanged': True, 'gpu': False, 'workers_per_job': 4, 'deadline_hours': 10.3}
pp = O / 'prepared_timing_abba_v10.json'; assert not pp.exists(); pp.write_text(json.dumps(prep, indent=2))
print(json.dumps(prep, indent=2))
