"""Freeze the P5 confirmation notebook from the development selection (v11 source, unchanged code).

Usage: python research_round14_build_template_confirmation.py
Reads research_round14_template_development_analysis_v1.json; refuses unless the pre-registered
selection advances. Grid = selected (kind, cap, E) x {right, left, wrong} + none x {right, left,
wrong} on the 16 confirmation regions; static tables are rebuilt from all 16 development regions
inside the job (cpu_round14_template.build_tables, role 'confirmation').
"""
from pathlib import Path
import ast, base64, hashlib, json, time, zipfile

R = Path(__file__).resolve().parent; O = R / 'kaggle_cpu_round14'


def h(b): return hashlib.sha256(b).hexdigest()


a = json.loads((R / 'research_round14_template_development_analysis_v1.json').read_text())
assert a['advances_to_confirmation'] is True, 'selection does not beat none-right: record the negative, no confirmation'
s = a['selected']; kind, cap, E = s['kind'], s['cap'], s['edit_cap']
grid = [[c, kind, cap, E] for c in ('right', 'left', 'wrong')] + [[c, 'none', 0, 0] for c in ('right', 'left', 'wrong')]
zp = O / 'sources_template_v11.zip'; blob = zp.read_bytes(); digest = h(blob)
assert digest == 'b80255f7b6965dfb79c6b76837613ebe8d3890aa5e3b508d68674c2eb0999374', 'confirmation must reuse the frozen v11 code'
slug = 'hutter-r14-template-confirmation-v1'; folder = O / slug; folder.mkdir()
main = """import os,sys,zipfile,io,base64,hashlib,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
raw=base64.b64decode(__BLOB__);assert hashlib.sha256(raw).hexdigest()==__SHA__
root=Path('/root/r14_code_template_v11');root.mkdir()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for e in json.loads(z.read('source_manifest.json')):
        p=(root/e['path']).resolve();assert p.is_relative_to(root);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
sys.path.insert(0,str(root))
from hutter_research.cpu_round14_template import main
if __name__=='__main__':main('confirmation',__GRID__,label='v1')
""".replace('__BLOB__', repr(base64.b64encode(blob).decode())).replace('__SHA__', repr(digest)).replace('__GRID__', repr(grid))
ast.parse(main); (folder / 'main.py').write_bytes(main.encode())
meta = {'id': 'chaoscpp/' + slug, 'title': slug, 'code_file': 'main.py', 'language': 'python', 'kernel_type': 'script',
        'is_private': True, 'enable_gpu': False, 'enable_tpu': False, 'enable_internet': False,
        'dataset_sources': ['chaoscpp/hutter-r13-four-lane-cpu-assets-v1'], 'competition_sources': [], 'kernel_sources': []}
(folder / 'kernel-metadata.json').write_text(json.dumps(meta, indent=2))
job = {'ref': meta['id'], 'folder': slug, 'main_sha256': h(main.encode()), 'workers': 4, 'role': 'confirmation', 'grid': grid, 'regions': 16}
kz = O / 'kernels_template_confirmation_v11.zip'; assert not kz.exists()
with zipfile.ZipFile(kz, 'x', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(folder.iterdir()): z.write(p, p.relative_to(O).as_posix())
prep = {'frozen': time.time(), 'jobs': [job], 'source_sha256': digest, 'selection': s,
        'development_analysis_sha256': h((R / 'research_round14_template_development_analysis_v1.json').read_bytes()),
        'protocol_sha256': h((R / 'research_round14_template_freeze_v1.md').read_bytes()), 'kernels_zip_sha256': h(kz.read_bytes()),
        'gpu': False, 'workers_per_job': 4, 'deadline_hours': 10.3}
pp = O / 'prepared_template_confirmation_v11.json'; assert not pp.exists(); pp.write_text(json.dumps(prep, indent=2))
print(json.dumps(prep, indent=2))
