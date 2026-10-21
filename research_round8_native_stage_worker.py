import datetime,hashlib,importlib.util,json,os,pathlib,shutil,subprocess,sys,time,traceback
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');D=R/'native_stage_trace_v1';D.mkdir(exist_ok=False);T=D/'tree';N=R/'atom_cache_v1'
m={'status':'RUNNING','pid':os.getpid(),'session':355735431,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'observation-only native staged channels, archive/Q16/independent decode gates; no candidate inference','core_retraining':False,'paid_spending_usd':0,'deletions':[],'controls':[],'exports':[]}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def run(cmd,cwd,env,label):
 start=time.monotonic()
 with (D/(label+'.log')).open('x') as f:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,s,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(s)
 a={'wall_seconds':time.monotonic()-start,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 if p.returncode:m['failed_runtime']=a;raise RuntimeError((label,a))
 return a
try:
 assert shutil.disk_usage(R).free>1_200_000_000
 nm=json.loads((N/'manifest.json').read_text());assert len(nm['controls'])==2 and len(nm['native_exports'])==4
 source=R/'native_hidden_trace_v1/tree';assert source.exists();shutil.copytree(source,T,symlinks=True,ignore=shutil.ignore_patterns('task_bin','*.o','cmix','cmix_hidden_trace'))
 pred=T/'src/predictor.cpp';text=pred.read_text();m['parent_predictor_sha256']=sha(pred)
 anchor='  float p = Sigmoid::Logistic(mixer_1_[0].Mix());\n  p = sse_.Predict(p);';assert text.count(anchor)==1
 text=text.replace(anchor,'  float p = Sigmoid::Logistic(mixer_1_[0].Mix());\n  const float hp_pre_sse_probability = p;\n  p = sse_.Predict(p);')
 anchor='  if (byte_mixer_override >= 0) {\n    return byte_mixer_override;\n  }\n  return p;';assert text.count(anchor)==1
 observation=r'''  if (const char* path = std::getenv("LAB_STAGETRACE")) {
    static FILE* hp_stage_file = std::fopen(path, "wbx");
    static unsigned int hp_stage_width = 0;
    const auto& inputs = layers_[1].Inputs();
    const unsigned int n = static_cast<unsigned int>(inputs.size());
    if (!hp_stage_file || n != 14) std::abort();
    if (!hp_stage_width) {
      hp_stage_width = n + 5;
      const unsigned char magic[8] = {'H','P','S','T','G','0','0','1'};
      if (std::fwrite(magic, 1, 8, hp_stage_file) != 8 ||
          std::fwrite(&hp_stage_width, 4, 1, hp_stage_file) != 1) std::abort();
    }
    float row[32] = {};
    for (unsigned int i = 0; i < n; ++i) row[i] = inputs[i];
    row[n] = hp_pre_sse_probability;
    row[n+1] = p;
    row[n+2] = byte_mixer_override >= 0 ? byte_mixer_override : p;
    row[n+3] = byte_mixer_output;
    row[n+4] = Sigmoid::Logistic(layers_[0].Inputs()[fxcm_model_index]);
    if (std::fwrite(row, 4, hp_stage_width, hp_stage_file) != hp_stage_width) std::abort();
  }
'''
 text=text.replace(anchor,observation+anchor);pred.write_text(text);m['patched_predictor_sha256']=sha(pred);m['source_hashes']=[{'file':f,'sha256':sha(R/f)} for f in ['research_round8_native_stage_worker.py','research_round8_native_stage_protocol.md','research_round8_native_hidden_trace_worker.py']];m['native_input_manifest_sha256']=sha(N/'manifest.json');m['production_stream']=nm['production_stream'];save('isolated observation patch applied; exact compiler readiness')
 sys.path.insert(0,str(P));spec=importlib.util.spec_from_file_location('hp_original_native_helper',R/'research_round8_native_hidden_trace_worker.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.DEST=D;helper.TREE=T
 compiler_path=helper.restore_compiler();env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_PREPARE','HP_LEX_'))};env['PATH']=compiler_path
 m['compiler']=subprocess.check_output(['clang++-17','--version'],text=True).splitlines()[0];m['classical_flags']=helper.FLAGS;m['transformer_flags']=helper.TF
 m['compile']=run(['make','-B','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+helper.FLAGS,'CFLAGS_TF_DEFINES='+helper.TF],T,env,'compile');binary=T/'cmix';assert binary.is_file();m['binary_sha256']=sha(binary)
 weights=P/'lex_audit/lex_h1_run11.tfwc2';dictionary=T/'dictionary/english.dic';assert sha(weights)==nm['weights_sha256'] and sha(dictionary)==nm['dictionary_sha256'];ee={**env,'LAB_RAW':'1','LAB_VOCAB':str(P/'preserved/data/vocab.bm'),'LAB_DICT':str(dictionary),'LAB_KEEP_TEMP':'1'}
 def encode(s,size,label):
  dest=D/label;dest.mkdir();(dest/'.dict').symlink_to(dictionary);raw=N/(s+('32k.bin' if size==32768 else '512k.bin'));out=dest/'out.cmx';qp=dest/'final_p.u16';stage=dest/'stage.f32';account=run([str(binary),'-n','--transformer',str(weights),str(raw),str(out)],dest,{**ee,'LAB_BITTRACE':str(qp),'LAB_STAGETRACE':str(stage)},label)
  with stage.open('rb') as f:header=f.read(12)
  assert stage.stat().st_size==12+size*8*19*4 and header[:8]==b'HPSTG001' and int.from_bytes(header[8:],'little')==19;frames=np.memmap(stage,dtype='<f4',mode='r',offset=12,shape=(size*8,19));assert np.isfinite(frames).all();assert qp.stat().st_size==size*16
  row={'slice':s,'size':size,'archive_sha256':sha(out),'final_p_sha256':sha(qp),'stage_sha256':sha(stage),'stage_bytes':stage.stat().st_size,'stage_columns':19,'accounting':account};return dest,row
 for s in 'ab':
  save('32K observer/reference/independent decode '+s);dest,row=encode(s,32768,s+'32k');old=N/(s+'32k_hidden');assert (dest/'out.cmx').read_bytes()==(old/'out.cmx').read_bytes() and (dest/'final_p.u16').read_bytes()==(old/'final_p.u16').read_bytes();decode=D/(s+'32k_decode');decode.mkdir();(decode/'.dict').symlink_to(dictionary);row['decode_accounting']=run([str(binary),'-d','--transformer',str(weights),str(dest/'out.cmx'),'decoded.bin'],decode,ee,s+'32k_decode');assert (decode/'decoded.bin').read_bytes()==(N/(s+'32k.bin')).read_bytes();row.update(archive_identity=True,Q16_identity=True,independent_decode_exact=True);m['controls'].append(row);save('32K gates PASS '+s)
 for s in 'ab':
  dest,row=encode(s,524288,s+'512k');v=next(v for v in nm['native_exports'] if v['slice']==s);assert row['archive_sha256']==v['archive_sha256'] and row['final_p_sha256']==v['final_p_sha256'];row.update(archive_identity=True,Q16_identity=True,input_sha256=v['input_sha256']);m['exports'].append(row);save('512K exact staged channels '+s)
 m.update(status='COMPLETE_NATIVE_STAGE_IDENTITY_AND_AB_EXPORTS',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('ready for separately registered source-disagreement residual; no C/D exports')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved; no duplicate launch');raise
