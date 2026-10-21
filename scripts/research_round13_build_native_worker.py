"""Checked isolated native integration; preserves every existing tree/binary."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time,traceback,zipfile
W=Path('/kaggle/working/hp_round13');OUT=W/'native_build_v1.json';ROOT=Path('/root/hp_round13_native_build_v1')
M={'status':'COPYING_ISOLATED_SOURCES','pid':os.getpid(),'started':time.time(),'deletions':[],
 'original_tree':'/kaggle/working/hp_round8/native_stage_trace_v1/tree','builds':[]}
def save():OUT.write_text(json.dumps(M,indent=2))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def replace_once(text,old,new,label):
    assert text.count(old)==1,(label,text.count(old));return text.replace(old,new)
try:
    assert not OUT.exists() and not ROOT.exists();save()
    source=Path(M['original_tree']);tree=ROOT/'tree';ROOT.mkdir()
    def ignored(folder,names):
        return [n for n in names if n.endswith(('.o','.profraw','.profdata')) or n in ('cmix','cmix.map','pgo_data','.git','data')]
    shutil.copytree(source,tree,ignore=ignored)
    header=tree/'src/predictor.h';cpp=tree/'src/predictor.cpp'
    text=header.read_text();text=replace_once(text,'  float Predict();','  float Predict();\n  unsigned int PredictQ16();','Predict public interface')
    text=replace_once(text,'#include "mixer/sigmoid.h"','#include "hp_r13/native_final_head.h"\n#include "mixer/sigmoid.h"','include')
    text=replace_once(text,'  Sigmoid sigmoid_;','  Sigmoid sigmoid_;\n  hp::NativeFinalHead hp_r13_head_;','head member');header.write_text(text)
    text=cpp.read_text()
    old='  if (byte_mixer_override >= 0) {\n    return byte_mixer_override;\n  }\n  return p;\n}'
    new='  hp_r13_head_.Capture(hp_pre_sse_probability, byte_mixer_output, layers_[1].Inputs(), layers_[1].Inputs().size());\n'+old
    text=replace_once(text,old,new,'capture native features')
    text=replace_once(text,'void Predictor::Perceive(int bit) {','unsigned int Predictor::PredictQ16() { return hp_r13_head_.Predict(Predict()); }\n\nvoid Predictor::Perceive(int bit) {\n  hp_r13_head_.Observe(bit);','observe each known or coded bit')
    marker='  // Trace belongs to the NEXT byte; reset rows cannot query stale activations.'
    text=replace_once(text,marker,'  hp_r13_head_.SetNextByteNeuralValid(!last_of_piece);\n'+marker,'neural validity');cpp.write_text(text)
    for relative in ('src/coder/encoder.cpp','src/coder/decoder.cpp'):
        p=tree/relative;text=p.read_text()
        text=replace_once(text,'const unsigned int p = Discretize(p_->Predict());','const unsigned int p = p_->PredictQ16();','direct Q16 '+relative)
        text=replace_once(text,'  p_->Predict();\n  p_->Perceive(bit);','  p_->PredictQ16();\n  p_->Perceive(bit);','known-bit path '+relative);p.write_text(text)
    code=tree/'src/hp_r13';code.mkdir()
    with zipfile.ZipFile(W/'native_head_sources_v1.zip') as z:
        for name in z.namelist():
            raw=z.read(name);(code/Path(name).name).write_bytes(raw)
    make=tree/'makefile';text=make.read_text();assert text.count('-fno-exceptions')==2
    text=text.replace('-fno-exceptions','-fexceptions');make.write_text(text)
    tools=ROOT/'tools';tools.mkdir();(tools/'ld.lld').symlink_to('/usr/bin/ld.lld-17')
    env=dict(os.environ);env['PATH']=str(tools)+':'+env['PATH']
    common='-DSEED=923 -DUPDATE_LIMIT=3000 -DPPMD_MEM_MB=3500 -DCMIX_L0_LR_SCALE=0.6 -DCMIX_L1_LR_SCALE=0.25 -DCMIX_L0_MIXER_MASK=0x42e72du -DFXCM_CM_DIV=2'
    tf='-DQMAT_CODEBOOK=1 -DQMAT_WMAX=21 -DQMAT_SMALL_W8=1 -DTF_ACTQ_DYN=1 -DTF_AVX512=1'
    M.update(status='BUILDING_FINITE_NATIVE_ARMS',source_changes=[str(p.relative_to(tree)) for p in (header,cpp,make,tree/'src/coder/encoder.cpp',tree/'src/coder/decoder.cpp')],
      flags={'common':common,'transformer':tf,'head_modes':[0,1,2]},compiler=subprocess.check_output(['clang++-17','--version'],text=True).splitlines()[0]);save()
    # PGO was not available; these are laboratory binaries. Compile work uses
    # four jobs briefly, then every subsequent archive gets separate CPU timing.
    binaries=W/'native_binaries_v1';binaries.mkdir(exist_ok=False)
    for mode in (0,1,2):
        start=time.time();log=W/f'native_build_mode_{mode}.log'
        with log.open('xb') as f:r=subprocess.run(['make','-j4','cmix','CFLAGS_DEFINES='+common+f' -DHP_R13_HEAD={mode}','CFLAGS_TF_DEFINES='+tf],cwd=tree,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
        assert r.returncode==0,(mode,r.returncode,log.read_text(errors='replace')[-3500:])
        binary=binaries/f'cmix_head_{mode}';shutil.copyfile(tree/'cmix',binary);binary.chmod(0o700)
        M['builds'].append({'mode':mode,'bytes':binary.stat().st_size,'sha256':sha(binary),'build_wall_seconds':time.time()-start});save()
    source_zip=W/'native_integration_sources_v1.zip'
    with zipfile.ZipFile(source_zip,'x',zipfile.ZIP_DEFLATED) as z:
        for p in tree.rglob('*'):
            if p.is_file() and (p.suffix in ('.h','.cpp','.inc') or p==make):
                z.write(p,str(p.relative_to(tree)))
    M.update(status='COMPLETE_LAB_BINARIES_AWAITING_PARITY_PREFLIGHT',finished=time.time(),source_zip_sha256=sha(source_zip));save()
except BaseException as e:
    M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc(),finished=time.time());save();raise
