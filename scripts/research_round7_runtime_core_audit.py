import pathlib,subprocess,hashlib,json,zipfile,importlib.metadata
out=pathlib.Path('/kaggle/working/hp_round7');dest=pathlib.Path('/root/hp/round7_runtime_packages')
assert not (out/'runtime_core_audit.json').exists(),'Refuse duplicate audit'
rc=subprocess.run(['python','-m','pip','download','--no-deps','--only-binary=:all:','--dest',str(dest),'fla-core==0.5.1','wadler-lindig==0.1.3'],timeout=180,capture_output=True,text=True)
print(rc.stdout);print(rc.stderr)
rows=[]
for p in dest.glob('*.whl'):
    if not p.name.startswith(('fla_core-','wadler_lindig-')):continue
    with zipfile.ZipFile(p) as z:metadata=z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))).decode()
    rows.append({'filename':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                 'requirements':[l for l in metadata.splitlines() if l.startswith(('Requires-Dist:','Requires-Python:'))]})
versions={}
for n in ['torch','triton','numpy','einops','packaging','transformers','ninja','termcolor']:
    try:versions[n]=importlib.metadata.version(n)
    except importlib.metadata.PackageNotFoundError:versions[n]=None
result={'returncode':rc.returncode,'files':rows,'installed_dependencies':versions,'scope':'Wheel/dependency inspection only; no installation, inference or SGD'}
(out/'runtime_core_audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
