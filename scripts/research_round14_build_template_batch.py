"""Freeze the P5 template development-screen notebook (v11). Never overwrites anything."""

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


def h(b): return hashlib.sha256(b).hexdigest()


zp = O / 'sources_template_v11.zip'; assert not zp.exists(); entries = []
with zipfile.ZipFile(zp, 'x', zipfile.ZIP_DEFLATED) as z:
    for p in sorted((project_path('hutter_research', base=R)).rglob('*')):
        if not p.is_file() or p.suffix not in ('.py', '.cpp', '.h', '.hpp', '.inc') or '__pycache__' in p.parts: continue
        b = p.read_bytes(); n = p.relative_to(R).as_posix()
        if p.suffix == '.py': ast.parse(b.decode('utf-8'))
        z.writestr(n, b); entries.append({'path': n, 'bytes': len(b), 'sha256': h(b)})
    z.writestr('source_manifest.json', json.dumps(entries, indent=2))
for need in ('hutter_research/template_codec.py', 'hutter_research/cpu_round14_template.py', 'hutter_research/constructor_codec.py'):
    assert any(e['path'] == need for e in entries), need
blob = zp.read_bytes(); digest = h(blob)
slug = 'hutter-r14-template-development-v1'; folder = O / slug; folder.mkdir()
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
if __name__=='__main__':main('development')
""".replace('__BLOB__', repr(base64.b64encode(blob).decode())).replace('__SHA__', repr(digest))
ast.parse(main); (folder / 'main.py').write_bytes(main.encode())
meta = {'id': 'chaoscpp/' + slug, 'title': slug, 'code_file': 'main.py', 'language': 'python', 'kernel_type': 'script',
        'is_private': True, 'enable_gpu': False, 'enable_tpu': False, 'enable_internet': False,
        'dataset_sources': ['chaoscpp/hutter-r13-four-lane-cpu-assets-v1'], 'competition_sources': [], 'kernel_sources': []}
(folder / 'kernel-metadata.json').write_text(json.dumps(meta, indent=2))
job = {'ref': meta['id'], 'folder': slug, 'main_sha256': h(main.encode()), 'workers': 4, 'role': 'development', 'arms': 39, 'regions': 16}
kz = O / 'kernels_template_v11.zip'; assert not kz.exists()
with zipfile.ZipFile(kz, 'x', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(folder.iterdir()): z.write(p, p.relative_to(O).as_posix())
prep = {'frozen': time.time(), 'jobs': [job], 'source_sha256': digest,
        'protocol_sha256': h((project_path('research_round14_template_freeze_v1.md', base=R)).read_bytes()),
        'kernels_zip_sha256': h(kz.read_bytes()), 'gpu': False, 'workers_per_job': 4, 'deadline_hours': 10.3}
pp = O / 'prepared_template_v11.json'; assert not pp.exists(); pp.write_text(json.dumps(prep, indent=2))
print(json.dumps(prep, indent=2))
