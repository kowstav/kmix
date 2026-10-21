"""Freeze the two P4 development notebooks (v13 = v12 + binary copy/chmod fix): D-A modes {1,2}, D-B modes {3,0}, regions {0,1,4,5}.
The v1 notebooks failed before any coding (PermissionError executing from the read-only dataset mount); they stay preserved."""
from pathlib import Path
import ast, base64, hashlib, json, sys, time, zipfile

R = Path(__file__).resolve().parent; O = R / 'kaggle_cpu_round14'
ASSET_MANIFEST_SHA = sys.argv[1]   # sha256 of structx_assets.json produced by the passing live gate


def h(b): return hashlib.sha256(b).hexdigest()


zp = O / 'sources_structx_v13.zip'; assert not zp.exists(); entries = []
with zipfile.ZipFile(zp, 'x', zipfile.ZIP_DEFLATED) as z:
    for p in sorted((R / 'hutter_research').rglob('*')):
        if not p.is_file() or p.suffix not in ('.py', '.cpp', '.h', '.hpp', '.inc') or '__pycache__' in p.parts: continue
        b = p.read_bytes(); n = p.relative_to(R).as_posix()
        if p.suffix == '.py': ast.parse(b.decode('utf-8'))
        z.writestr(n, b); entries.append({'path': n, 'bytes': len(b), 'sha256': h(b)})
    z.writestr('source_manifest.json', json.dumps(entries, indent=2))
for need in ('hutter_research/cpu_round14_structx.py', 'hutter_research/structx_lex.h', 'hutter_research/structx_lex_patch.py'):
    assert any(e['path'] == need for e in entries), need
blob = zp.read_bytes(); digest = h(blob); jobs = []
for tag, modes in (('a', (1, 2)), ('b', (3, 0))):
    slug = f'hutter-r14-structx-development-{tag}-v2'; folder = O / slug; folder.mkdir()
    main = """import os,sys,zipfile,io,base64,hashlib,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
raw=base64.b64decode(__BLOB__);assert hashlib.sha256(raw).hexdigest()==__SHA__
root=Path('/root/r14_code_structx_v13');root.mkdir()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for e in json.loads(z.read('source_manifest.json')):
        p=(root/e['path']).resolve();assert p.is_relative_to(root);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
sys.path.insert(0,str(root))
m=list(Path('/kaggle/input').rglob('structx_assets.json'));assert len(m)==1 and hashlib.sha256(m[0].read_bytes()).hexdigest()==__AMS__
from hutter_research.cpu_round14_structx import main
if __name__=='__main__':main('development',__MODES__,[0,1,4,5],label=__LABEL__)
""".replace('__BLOB__', repr(base64.b64encode(blob).decode())).replace('__SHA__', repr(digest)).replace(
        '__AMS__', repr(ASSET_MANIFEST_SHA)).replace('__MODES__', repr(modes)).replace('__LABEL__', repr('d' + tag + '2'))
    ast.parse(main); (folder / 'main.py').write_bytes(main.encode())
    meta = {'id': 'chaoscpp/' + slug, 'title': slug, 'code_file': 'main.py', 'language': 'python', 'kernel_type': 'script',
            'is_private': True, 'enable_gpu': False, 'enable_tpu': False, 'enable_internet': False,
            'dataset_sources': ['chaoscpp/hutter-r14-structx-assets-v1'], 'competition_sources': [], 'kernel_sources': []}
    (folder / 'kernel-metadata.json').write_text(json.dumps(meta, indent=2))
    jobs.append({'ref': meta['id'], 'folder': slug, 'main_sha256': h(main.encode()), 'workers': 4, 'modes': list(modes),
                 'region_ids': [0, 1, 4, 5], 'role': 'development'})
kz = O / 'kernels_structx_v13.zip'; assert not kz.exists()
with zipfile.ZipFile(kz, 'x', zipfile.ZIP_DEFLATED) as z:
    for j in jobs:
        for p in sorted((O / j['folder']).iterdir()): z.write(p, p.relative_to(O).as_posix())
prep = {'frozen': time.time(), 'jobs': jobs, 'source_sha256': digest, 'asset_manifest_sha256': ASSET_MANIFEST_SHA,
        'protocol_sha256': h((R / 'research_round14_structx_freeze_v1.md').read_bytes()),
        'addendum_sha256': h((R / 'research_round14_structx_freeze_v1_addendum_v13.md').read_bytes()), 'kernels_zip_sha256': h(kz.read_bytes()),
        'gpu': False, 'workers_per_job': 4, 'deadline_hours': 10.3}
pp = O / 'prepared_structx_v13.json'; assert not pp.exists(); pp.write_text(json.dumps(prep, indent=2))
print(json.dumps(prep, indent=2))
