import pathlib,subprocess,shutil,json,hashlib,time
out=pathlib.Path('/kaggle/working/hp_round7');old=pathlib.Path('/root/hp/lex_roundtrip_lab');dest=pathlib.Path('/root/hp/lex_codebook_lab')
assert not dest.exists();shutil.copytree(old,dest)
flags='-DSEED=923 -DUPDATE_LIMIT=3000 -DPPMD_MEM_MB=3500 -DCMIX_L0_LR_SCALE=0.6 -DCMIX_L1_LR_SCALE=0.25 -DCMIX_L0_MIXER_MASK=0x42e72du -DFXCM_CM_DIV=2'
tf='-DQMAT_CODEBOOK=1 -DQMAT_WMAX=21 -DQMAT_SMALL_W8=1 -DTF_ACTQ_DYN=1 -DTF_AVX512=1'
started=time.monotonic()
with (out/'lex_codebook_build.log').open('w') as f:
    subprocess.run(['make','-B','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+flags,'CFLAGS_TF_DEFINES='+tf],cwd=dest,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=1500)
binary=out/'cmix_round7_lex_codebook';shutil.copy2(dest/'cmix',binary)
row={'binary_bytes':binary.stat().st_size,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'classical_defines':flags,'actual_inference_macros':tf,'published_option_translation':'TF_CODEBOOK -> QMAT_CODEBOOK/QMAT_WMAX; TF_SMALL_W8 -> QMAT_SMALL_W8; TF_ACTQ_DYN and TF_AVX512 unchanged','compiler':subprocess.check_output(['clang++-17','--version'],text=True).splitlines()[0],'forced_all_objects_recompiled':True,'build_seconds':time.monotonic()-started,'pgo':False,'lto':False,'native_validation':'pending','initial_builds_rejected':'wrapper option names were mistakenly used as inference macros; native quantization range check rejected before coding; old binaries/results not competitive baseline evidence','weight_sha256':hashlib.sha256((dest/'models/lex_h1_run11.tfwc2').read_bytes()).hexdigest()}
(out/'lex_codebook_build_results.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
