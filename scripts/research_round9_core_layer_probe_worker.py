"""Capture native FP32 priors and per-layer activations to repair GPU parity."""
import pathlib,subprocess,os,json,time,hashlib,traceback,shutil,sys,importlib.util
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'core_layer_probe_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/core_layer_probe_v1');S.mkdir(exist_ok=False);T=S/'tree';m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'deletions':[],'spending_usd':0,'scope':'observation-only native FP32 layer and prior capture; no neural/model update change'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
try:
 parent=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree');shutil.copytree(parent,T,symlinks=True,ignore=shutil.ignore_patterns('task_bin','*.o','cmix','cmix_hidden_trace'))
 p=T/'cpp_infer/src/opt/model_opt.cpp';src=p.read_text()
 def replace(a,b):
  global src
  assert src.count(a)==1,(a,src.count(a));src=src.replace(a,b)
 replace('  void step(uint8_t token, float* probs_out) {','''  void step(uint8_t token, float* probs_out) {
    static FILE* hp_probe = nullptr;
    static unsigned long long hp_probe_rows = 0;
    bool hp_write = false;
    if (const char* path = std::getenv("HP_CORE_LAYER_PROBE")) {
      if (!hp_probe) {hp_probe=std::fopen(path,"wbx");if(!hp_probe)std::abort();}
      hp_write = hp_probe_rows < 4096;
      if(hp_write) {std::fwrite(&token,1,1,hp_probe);std::fwrite(prior_f32,4,205,hp_probe);}
    }''')
 replace('      embed_combine192(tok, yb, x);  // x0 = tok_row + rms_norm(prior_y)','''      embed_combine192(tok, yb, x);  // x0 = tok_row + rms_norm(prior_y)
      if(hp_write)std::fwrite(x,4,192,hp_probe);''')
 replace('      mlp_block(l);','''      mlp_block(l);
      if(hp_write)std::fwrite(x,4,192,hp_probe);''')
 replace('      std::memcpy(probs_out, probs208, sizeof(float) * V);','''      std::memcpy(probs_out, probs208, sizeof(float) * V);
      if(hp_write){std::fwrite(probs208,4,205,hp_probe);hp_probe_rows++;std::fflush(hp_probe);}''')
 p.write_text(src);m['observer_source_sha256']=sha(p)
 sys.path.insert(0,'/kaggle/working/hp_round7');spec=importlib.util.spec_from_file_location('helper',pathlib.Path('/kaggle/working/hp_round8/research_round8_native_hidden_trace_worker.py'));h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.DEST=D;h.TREE=T;path=h.restore_compiler();env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','HP_CORE_','FX_PREPARE'))};env['PATH']=path;save('building observation-only layer capture')
 t=time.monotonic()
 with (D/'build.log').open('w') as f:subprocess.run(['make','-B','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+h.FLAGS,'CFLAGS_TF_DEFINES='+h.TF],cwd=T,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 m['build_seconds']=time.monotonic()-t;data=pathlib.Path('/root/hp_round9/core_data_v2');raw=(data/'input.bin').read_bytes()[:8192];(S/'input.bin').write_bytes(raw);(S/'.dict').symlink_to(T/'dictionary/english.dic');m['native_input_sha256']=sha(S/'input.bin');weights=pathlib.Path('/kaggle/working/hp_round7/lex_audit/lex_h1_run11.tfwc2');env.update(LAB_RAW='1',LAB_VOCAB='/kaggle/working/hp_round7/preserved/data/vocab.bm',LAB_DICT=str(S/'.dict'),LAB_KEEP_TEMP='1');save('capturing native initial embedding and12blocks with exact FP32 priors')
 cmd=[str(T/'cmix'),'-n','--transformer-only','--transformer',str(weights),'--save-transformer-probs',str(S/'neural.f16'),str(S/'input.bin'),str(S/'out.cmx')]
 with (D/'native.log').open('w') as f:subprocess.run(cmd,cwd=S,env={**env,'HP_CORE_LAYER_PROBE':str(S/'layers.bin')},stdout=f,stderr=subprocess.STDOUT,check=True)
 # Observer control must reproduce the existing first8192 native NN rows.
 expected=(data/'native_nn.f16').read_bytes()[:8192*205*2];assert (S/'neural.f16').read_bytes()==expected;m['native_neural_observer_identity']='PASS';rowbytes=1+4*(205+13*192+205);assert (S/'layers.bin').stat().st_size%rowbytes==0;m['rows']=(S/'layers.bin').stat().st_size//rowbytes;m['row_bytes']=rowbytes;m['layer_file_sha256']=sha(S/'layers.bin');m.update(status='COMPLETE_NATIVE_CORE_LAYER_OBSERVATION',finished=time.time(),scratch=str(S));save('native FP32 layer observations ready; GPU differential comparison pending')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
