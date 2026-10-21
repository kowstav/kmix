"""Download only the source-declared small runtime wheels and inspect requirements.

No dependency resolver upgrade, installation, model execution or SGD.
"""
import pathlib,subprocess,hashlib,json,zipfile,time
out=pathlib.Path('/kaggle/working/hp_round7');dest=pathlib.Path('/root/hp/round7_runtime_packages');dest.mkdir(parents=True,exist_ok=False)
args=['python','-m','pip','download','--no-deps','--only-binary=:all:','--dest',str(dest),'flash-linear-attention==0.5.1','jaxtyping==0.3.11']
start=time.monotonic();rc=subprocess.run(args,timeout=180).returncode
rows=[]
for p in dest.glob('*.whl'):
    with zipfile.ZipFile(p) as z:
        metadata=z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))).decode()
    rows.append({'filename':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                 'requires':[line for line in metadata.splitlines() if line.startswith(('Requires-Dist:','Requires-Python:'))]})
result={'returncode':rc,'wall_seconds':time.monotonic()-start,'files':rows,'source_pin':'Preserved project pyproject.toml minimum versions selected exactly',
        'scope':'Dependency readiness only; no installations, GPU model inference, training, deletions or rental'}
(out/'runtime_package_audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
assert rc==0,'Pinned wheels unavailable; preserve failure and inspect before choosing any fallback'
