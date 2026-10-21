"""Restore a matched instrumentation build; existing sources remain untouched."""
import pathlib,subprocess,urllib.request,shutil,os,json,time
hp=pathlib.Path('/root/hp'); out=pathlib.Path('/kaggle/working/hp_round7')
def run(command,cwd=None,timeout=600):
    print(json.dumps({'command':command,'cwd':str(cwd) if cwd else None}),flush=True)
    subprocess.run(command,cwd=cwd,check=True,timeout=timeout)
if not shutil.which('clang++-17'):
    release='https://apt.llvm.org/jammy/dists/llvm-toolchain-jammy-17/Release'
    with urllib.request.urlopen(release,timeout=30) as r:
        if r.status!=200: raise RuntimeError('Pinned LLVM17 repository unavailable')
    key=pathlib.Path('/usr/share/keyrings/hp-llvm17.asc')
    with urllib.request.urlopen('https://apt.llvm.org/llvm-snapshot.gpg.key',timeout=30) as r: key.write_bytes(r.read())
    pathlib.Path('/etc/apt/sources.list.d/hp-llvm17.list').write_text('deb [signed-by=/usr/share/keyrings/hp-llvm17.asc] https://apt.llvm.org/jammy/ llvm-toolchain-jammy-17 main\n')
    run(['apt-get','update'],timeout=300)
    run(['apt-get','install','-y','--no-install-recommends','clang-17','make'],timeout=600)
lab=hp/'round7_lab'
if lab.exists(): raise RuntimeError('Refusing to overwrite an existing lab build')
shutil.copytree(hp/'src/fx2-cmix-transformer-v1',lab,ignore=shutil.ignore_patterns('.git','models','pgo_data','prof_input','__pycache__','run'))
run(['python',str(hp/'tools/labpatch.py')],cwd=lab)
run(['python',str(hp/'tools/lexpatch.py')],cwd=lab)
# Keep object files for small, isolated follow-up patches.
mf=lab/'makefile'; s=mf.read_text(); s=s.replace('\trm -f *.o\n','\t@true\n'); mf.write_text(s)
run(['make','-j2','CC=clang++-17'],cwd=lab)
shutil.copyfile(lab/'cmix',out/'cmix_round7_baseline'); shutil.copymode(lab/'cmix',out/'cmix_round7_baseline')
(hp/'lexT').mkdir(exist_ok=True)
(hp/'lexT/cmix').symlink_to(lab/'cmix')
print(json.dumps({'build_complete':True,'binary_bytes':(lab/'cmix').stat().st_size,'compiler':subprocess.check_output(['clang++-17','--version'],text=True).splitlines()[0]}),flush=True)
