"""Restore and instrument an isolated lexth11c baseline; no original overwrites."""
import pathlib,tarfile,subprocess,urllib.request,shutil,json,time,hashlib
out=pathlib.Path('/kaggle/working/hp_round7');dest=pathlib.Path('/root/hp/lex_baseline_lab')
assert not dest.exists(),'Refuse duplicate build / overwrite'
dest.mkdir(parents=True)
prefix='src/cmix-lex-transformer/'
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    selected=[m for m in tar.getmembers() if m.name.startswith(prefix)]
    for m in selected:
        relative=m.name[len(prefix):]
        if not relative:continue
        target=(dest/relative).resolve()
        assert target.is_relative_to(dest.resolve()),m.name
        if m.issym() or m.islnk():
            link=(target.parent/m.linkname).resolve()
            assert link.is_relative_to(dest.resolve()),m.name
        assert m.isfile() or m.isdir() or m.issym() or m.islnk(),m.name
    for m in selected:
        relative=m.name[len(prefix):]
        if not relative:continue
        m.name=relative;tar.extract(m,dest,filter='data')
    patch=tar.extractfile('tools/labpatch.py').read().decode()
if not shutil.which('clang++-17'):
    key=pathlib.Path('/usr/share/keyrings/hp-llvm17.asc')
    with urllib.request.urlopen('https://apt.llvm.org/llvm-snapshot.gpg.key',timeout=30) as r:key.write_bytes(r.read())
    pathlib.Path('/etc/apt/sources.list.d/hp-llvm17.list').write_text('deb [signed-by=/usr/share/keyrings/hp-llvm17.asc] https://apt.llvm.org/jammy/ llvm-toolchain-jammy-17 main\n')
    subprocess.run(['apt-get','update'],check=True,timeout=300)
    subprocess.run(['apt-get','install','-y','--no-install-recommends','clang-17','lld-17','make'],check=True,timeout=600)
# Restrict instrumentation to encoder and runner. Do not alter predictor topology.
patch=patch.split('# ---- predictor:')[0]+'# keep .dict'+patch.split('# keep .dict')[1].split('# LAB_UNIFORM_NN')[0]
script=dest/'round7_lex_labpatch.py';script.write_text(patch)
subprocess.run(['python',str(script)],cwd=dest,check=True)
mf=dest/'makefile';text=mf.read_text();text=text.replace('\trm -f *.o\n','\t@true\n');mf.write_text(text)
flags='-DSEED=923 -DUPDATE_LIMIT=3000 -DPPMD_MEM_MB=3500 -DCMIX_L0_LR_SCALE=0.6 -DCMIX_L1_LR_SCALE=0.25 -DCMIX_L0_MIXER_MASK=0x42e72du -DFXCM_CM_DIV=2'
tf='-DQMAT_CODEBOOK=1 -DQMAT_WMAX=21 -DQMAT_SMALL_W8=1 -DTF_ACTQ_DYN=1 -DTF_AVX512=1'
started=time.monotonic()
subprocess.run(['make','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+flags,'CFLAGS_TF_DEFINES='+tf],cwd=dest,check=True,timeout=1500)
binary=out/'cmix_round7_lex_baseline';shutil.copy2(dest/'cmix',binary)
row={'binary_bytes':binary.stat().st_size,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'compiler':subprocess.check_output(['clang++-17','--version'],text=True).splitlines()[0],'classical_defines':flags,'transformer_defines':tf,'build_seconds':time.monotonic()-started,'pgo':False,'lto':False,'instrumentation':'forced vocabulary/raw WRT/dictionary pretraining and per-byte final costs; no predictor topology edits','original_checkpoint_sha256':hashlib.sha256((dest/'models/lex_h1_run11.tfwc2').read_bytes()).hexdigest(),'no_neural_training':True,'no_deletion':True,'scope':'Matched laboratory build, not a reproduced PGO record executable or full archive'}
(out/'lex_build_results.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
print('LEX_BUILD_COMPLETE',flush=True)
