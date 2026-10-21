from pathlib import Path
import hashlib,json,os,shutil,subprocess,time,traceback,zipfile
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_native_cpu');M={'status':'WAITING_FOR_PINNED_COMPILER','started':time.time(),'builds':[],'deletions':[]}
def save():(W/'native_cpu_build_v1.json').write_text(json.dumps(M,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace(text,old,new):assert text.count(old)==1,(old,text.count(old));return text.replace(old,new)
try:
    assert not R.exists() and not (W/'native_cpu_build_v1.json').exists();R.mkdir();save()
    while True:
        p=W/'compiler_restore_v1.json'
        m=json.loads(p.read_text()) if p.exists() else {}
        if m.get('status','').startswith('FAIL'):raise RuntimeError('compiler restoration failed; inspect original manifest')
        if m.get('status')=='COMPLETE_PINNED_COMPILER_AVAILABLE':break
        time.sleep(20)
    source=Path('/kaggle/working/hp_round13/native_integration_sources_v1.zip')
    assert sha(source)=='9a593b335861569a7c720df0e8e76d85715deb971588b003a714d181e2b42662'
    tree=R/'tree';tree.mkdir()
    with zipfile.ZipFile(source) as z:
        for n in z.namelist():assert (tree/n).resolve().is_relative_to(tree)
        z.extractall(tree)
    p=tree/'src/predictor.cpp';s=p.read_text()
    s=replace(s,'  AddWord();','  if (HP_R14_ABLATION != 1) AddWord();')
    s=replace(s,'  AddMatch();','  if (HP_R14_ABLATION != 2) AddMatch();')
    s=replace(s,'  AddDoubleIndirect();','  if (HP_R14_ABLATION != 3) AddDoubleIndirect();')
    old='    FloatsToHalves(transformer_probs_.data(), half_scratch_.data(),\n        kTransformerVocabSize);\n    HalvesToFloats(half_scratch_.data(), transformer_probs_.data(),\n        kTransformerVocabSize);'
    s=replace(s,old,'#if !HP_R14_OUTPUT_FP32\n'+old+'\n#else\n    if (transformer_probs_writer_) Fail("FP32 candidate cannot emit legacy half probability rows");\n#endif')
    s='#ifndef HP_R14_ABLATION\n#define HP_R14_ABLATION 0\n#endif\n#ifndef HP_R14_OUTPUT_FP32\n#define HP_R14_OUTPUT_FP32 0\n#endif\n'+s;p.write_text(s)
    tools=R/'tools';tools.mkdir();(tools/'ld.lld').symlink_to('/usr/bin/ld.lld-17');env=dict(os.environ,PATH=str(tools)+':'+os.environ['PATH'])
    common='-DSEED=923 -DUPDATE_LIMIT=3000 -DPPMD_MEM_MB=3500 -DCMIX_L0_LR_SCALE=0.6 -DCMIX_L1_LR_SCALE=0.25 -DCMIX_L0_MIXER_MASK=0x42e72du -DFXCM_CM_DIV=2 -DHP_R13_HEAD=0'
    tf='-DQMAT_CODEBOOK=1 -DQMAT_WMAX=21 -DQMAT_SMALL_W8=1 -DTF_ACTQ_DYN=1 -DTF_AVX512=1'
    out=W/'native_cpu_binaries_v1';out.mkdir();M.update(status='BUILDING_FIVE_CONTROLLED_BINARIES',flags={'common':common,'transformer':tf},compiler=subprocess.check_output(['clang++-17','--version'],text=True).splitlines()[0]);save()
    for name,ablation,precision in [('neutral',0,0),('prune_word',1,0),('prune_match',2,0),('prune_indirect',3,0),('output_fp32',0,1)]:
        start=time.time();flags=common+f' -DHP_R14_ABLATION={ablation} -DHP_R14_OUTPUT_FP32={precision}'
        command=['make','-j4','cmix','CFLAGS_DEFINES='+flags,'CFLAGS_TF_DEFINES='+tf]
        with (W/('native_cpu_build_'+name+'.log')).open('xb') as f:r=subprocess.run(command,cwd=tree,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
        assert r.returncode==0,(name,r.returncode)
        target=out/('cmix_'+name);shutil.copyfile(tree/'cmix',target);target.chmod(0o700)
        M['builds'].append({'name':name,'bytes':target.stat().st_size,'sha256':sha(target),'command':command,'build_wall_seconds':time.time()-start});save()
    source_zip=W/'native_cpu_sources_v1.zip'
    with zipfile.ZipFile(source_zip,'x',zipfile.ZIP_DEFLATED) as z:
        for p in tree.rglob('*'):
            if p.is_file() and (p.suffix in ('.h','.cpp','.inc') or p.name=='makefile'):z.write(p,p.relative_to(tree).as_posix())
    M.update(status='COMPLETE_AWAITING_NATIVE_PARITY',finished=time.time(),source_sha256=sha(source_zip));save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
