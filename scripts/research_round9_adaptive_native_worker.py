import pathlib,json,os,sys,time,hashlib,traceback,subprocess,shutil,importlib.util
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round8');OUT=pathlib.Path('/kaggle/working/hp_round9');D=OUT/'adaptive_native_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/adaptive_native_v1');S.mkdir(exist_ok=False);T=S/'tree'
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scope':'frozen causal5expert adaptive correction on new G/H native archives and independent decode','spending_usd':0,'deletions':[],'controls':[],'candidates':[],'scratch':str(S),'offsets':{'g':65000000,'h':375000000},'full_package_qualified':False}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while chunk:=f.read(1<<20):h.update(chunk)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def run(cmd,cwd,env,label):
 t=time.monotonic()
 with (D/(label+'.log')).open('w') as f:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 a={'wall_seconds':time.monotonic()-t,'CPU_user_seconds':u.ru_utime,'CPU_system_seconds':u.ru_stime,'whole_peak_RSS_KiB':u.ru_maxrss,'returncode':p.returncode}
 if p.returncode:raise RuntimeError((label,a))
 return a
def patch(p,a,b):s=p.read_text();assert s.count(a)==1,(p,a[:80]);p.write_text(s.replace(a,b))
try:
 selected=json.loads((OUT/'adaptive_source_v1/manifest.json').read_text());assert selected['status']=='COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY';assert selected['frozen_policy_before_confirmation']['family']=='scaled5' and selected['frozen_policy_before_confirmation']['H_bits']==262144;m['frozen_policy']=selected['frozen_policy_before_confirmation'];m['selected_replay_sha256']=sha(OUT/'adaptive_source_v1/manifest.json');m['worker_sha256']=sha(OUT/'research_round9_adaptive_native_worker.py');m['protocol_sha256']=sha(OUT/'research_round9_adaptive_native_protocol.md')
 shutil.copytree(R/'native_inline_wide_v1/tree',T,symlinks=True,ignore=shutil.ignore_patterns('task_bin','*.o','cmix','cmix_hidden_trace'));header=T/'src/predictor.h';pred=T/'src/predictor.cpp'
 patch(header,'  bool hp_final_residual_valid_ = false;','  double hp_adaptive_weights_[5] = {0.2,0.2,0.2,0.2,0.2};\n  unsigned int hp_adaptive_experts_[5] = {};\n  bool hp_adaptive_pending_ = false;\n  bool hp_final_residual_valid_ = false;')
 patch(header,'  unsigned int ExternalFinalQ16(unsigned int native_p);','  unsigned int ExternalFinalQ16(unsigned int native_p);\n  void ExternalFinalObserve(int bit);')
 old='''  const double z = ell + dot;
  const double prob = z >= 0 ? 1.0/(1.0+std::exp(-z)) : std::exp(z)/(1.0+std::exp(z));
  return static_cast<unsigned int>(std::max(1.0,std::min(65535.0,std::floor(65536.0*prob+0.5))));'''
 new='''  const double multipliers[4] = {0.5,1.0,1.5,2.0};
  hp_adaptive_experts_[0] = native_p;
  double mixture = hp_adaptive_weights_[0] * double(native_p) / 65536.0;
  for (int k=1;k<5;k++) {
    const double z = ell + multipliers[k-1]*dot;
    const double prob = z >= 0 ? 1.0/(1.0+std::exp(-z)) : std::exp(z)/(1.0+std::exp(z));
    hp_adaptive_experts_[k] = static_cast<unsigned int>(std::max(1.0,std::min(65535.0,std::floor(65536.0*prob+0.5))));
    mixture += hp_adaptive_weights_[k] * double(hp_adaptive_experts_[k]) / 65536.0;
  }
  hp_adaptive_pending_ = true;
  return static_cast<unsigned int>(std::max(1.0,std::min(65535.0,std::floor(65536.0*mixture+0.5))));'''
 patch(pred,old,new)
 with pred.open('a') as f:f.write('''
void Predictor::ExternalFinalObserve(int bit) {
  if (!hp_adaptive_pending_) return;
  constexpr double epsilon = 2.6441431586476938e-06;
  double total = 0.0;
  for (int k=0;k<5;k++) {
    const double pk = bit ? double(hp_adaptive_experts_[k])/65536.0 : 1.0-double(hp_adaptive_experts_[k])/65536.0;
    hp_adaptive_weights_[k] *= pk; total += hp_adaptive_weights_[k];
  }
  for (int k=0;k<5;k++) hp_adaptive_weights_[k] = (1.0-epsilon)*hp_adaptive_weights_[k]/total+epsilon/5.0;
  hp_adaptive_pending_ = false;
}
''')
 for p in [T/'src/coder/encoder.cpp',T/'src/coder/decoder.cpp']:
  text=p.read_text();anchor='  p_->Perceive(bit);';at=text.find(anchor);assert at>=0;text=text[:at]+text[at:].replace(anchor,'  p_->ExternalFinalObserve(bit);\n'+anchor,1);p.write_text(text)
 m['changed_sources']=[{'file':str(p.relative_to(T)),'sha256':sha(p)} for p in [header,pred,T/'src/coder/encoder.cpp',T/'src/coder/decoder.cpp']];save('frozen adaptive prediction/update installed into actual native coder')
 sys.path.insert(0,'/kaggle/working/hp_round7');spec=importlib.util.spec_from_file_location('original_helper',R/'research_round8_native_hidden_trace_worker.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.DEST=D;helper.TREE=T;compiler_path=helper.restore_compiler();env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_PREPARE','HP_LEX_'))};env['PATH']=compiler_path
 m['build_accounting']=run(['make','-B','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+helper.FLAGS,'CFLAGS_TF_DEFINES='+helper.TF],T,env,'compile');binary=T/'cmix';teacher=R/'native_stage_trace_v1/tree/cmix';m['binary']={'bytes':binary.stat().st_size,'sha256':sha(binary),'lab_delta_vs_teacher':binary.stat().st_size-teacher.stat().st_size};weights=pathlib.Path('/kaggle/working/hp_round7/lex_audit/lex_h1_run11.tfwc2');dictionary=T/'dictionary/english.dic';base={**env,'LAB_RAW':'1','LAB_VOCAB':'/kaggle/working/hp_round7/preserved/data/vocab.bm','LAB_DICT':str(dictionary),'LAB_KEEP_TEMP':'1'}
 # Load only the independently specified replay function; parent worker isn't executed.
 import ast
 nodes=ast.parse((OUT/'research_round9_adaptive_source_worker.py').read_text());functions=[n for n in nodes.body if isinstance(n,ast.FunctionDef) and n.name=='replay'];assert len(functions)==1
 from numba import njit
 ns={'np':np,'math':__import__('math'),'njit':njit};exec(compile(ast.Module(body=functions,type_ignores=[]),'<frozen-replay>','exec'),ns);replay=ns['replay']
 from scipy.special import expit
 def decode(raw,out,label,extra,reference_p,reference_hidden):
  dd=S/(label+'_decode');dd.mkdir();(dd/'.dict').symlink_to(dictionary);dq=dd/'final_p.u16';dh=dd/'hidden.q8';a=run([str(binary),'-d','--transformer',str(weights),str(out),'decoded.bin'],dd,{**base,**extra,'LAB_DECODE_BITTRACE':str(dq),'LAB_HIDDENTRACE':str(dh)},label+'_decode');assert sha(dd/'decoded.bin')==sha(raw);assert sha(dq)==sha(reference_p) and sha(dh)==sha(reference_hidden);return a
 # Neutral update contract on a previously observed short control.
 dd=S/'a32k_zero';dd.mkdir();(dd/'.dict').symlink_to(dictionary);raw=R/'atom_cache_v1/a32k.bin';qp=dd/'final_p.u16';hp=dd/'hidden.q8';out=dd/'out.cmx';extra={'LAB_FINAL_RESIDUAL_ZERO':'1'};save('neutral native control')
 account=run([str(binary),'-n','--transformer',str(weights),str(raw),str(out)],dd,{**base,**extra,'LAB_BITTRACE':str(qp),'LAB_HIDDENTRACE':str(hp)},'a32k_zero_encode');ref=R/'atom_cache_v1/a32k_hidden';assert sha(out)==sha(ref/'out.cmx') and sha(qp)==sha(ref/'final_p.u16') and sha(hp)==sha(ref/'hidden.q8');da=decode(raw,out,'a32k_zero',extra,qp,hp);m['controls'].append({'neutral_archive_CDF_hidden_identity':True,'independent_decode_exact':True,'encode_accounting':account,'decode_accounting':da});save('neutral native control PASS')
 stream=R/'lexical_full_prepare_v1/lexical_full_ready.wrt'
 for s,offset in m['offsets'].items():
  td=S/(s+'_teacher');td.mkdir();(td/'.dict').symlink_to(dictionary)
  with stream.open('rb') as f:f.seek(offset);data=f.read(524288)
  raw=td/'input.bin';raw.write_bytes(data);tp=td/'final_p.u16';th=td/'hidden.q8';stage=td/'stage.f32';tout=td/'out.cmx';save('fresh '+s+' native teacher observation')
  ta=run([str(teacher),'-n','--transformer',str(weights),str(raw),str(tout)],td,{**base,'LAB_BITTRACE':str(tp),'LAB_HIDDENTRACE':str(th),'LAB_STAGETRACE':str(stage)},s+'_teacher');p=np.fromfile(tp,'<u2');ell=np.log(p.astype(np.float64)/(65536-p.astype(np.float64)));h=np.memmap(th,'u1','r',shape=(len(data),193));valid=np.repeat(np.r_[0,h[:-1,0]],8);st=np.memmap(stage,'<f4','r',offset=12,shape=(len(p),19));nn=np.clip(st[:,17].astype(np.float64),1/65536,65535/65536);feat=(np.clip(np.log(nn/(1-nn))-ell,-12,12)/12).astype(np.float32)*valid;dot=.0016181118716570748-.007454085408717222*ell+2.3818512619982752*feat;ex=np.column_stack([p,*[np.clip(np.floor(65536*expit(ell+a*dot)+.5),1,65535).astype('<u2') for a in [.5,1.,1.5,2.]]]);y=((np.frombuffer(data,'u1')[:,None]>>(7-np.arange(8)))&1).reshape(-1);q,ideal,rounded,like=replay(ex,y,2.6441431586476938e-06);expected=hashlib.sha256(q.tobytes()).hexdigest()
  cd=S/(s+'_candidate');cd.mkdir();(cd/'.dict').symlink_to(dictionary);out=cd/'out.cmx';qp=cd/'final_p.u16';hp=cd/'hidden.q8';save('fresh '+s+' actual adaptive native encode');ea=run([str(binary),'-n','--transformer',str(weights),str(raw),str(out)],cd,{**base,'LAB_BITTRACE':str(qp),'LAB_HIDDENTRACE':str(hp)},s+'_candidate_encode');assert sha(qp)==expected,(s,'native replay CDF mismatch');assert sha(hp)==sha(th),(s,'core trajectory changed');da=decode(raw,out,s+'_candidate',{},qp,hp)
  row={'slice':s,'offset':offset,'input_sha256':sha(raw),'teacher_archive_bytes':tout.stat().st_size,'candidate_archive_bytes':out.stat().st_size,'actual_archive_saving_bytes':tout.stat().st_size-out.stat().st_size,'candidate_archive_sha256':sha(out),'native_Q16_matches_frozen_replay':True,'core_hidden_identity':True,'independent_decode_exact':True,'encode_decode_Q16_hidden_identity':True,'teacher_accounting':ta,'candidate_encode_accounting':ea,'candidate_decode_accounting':da,'rounding_tax_bits':rounded-ideal,'candidate_Q16_sha256':sha(qp)};m['candidates'].append(row);save('all '+s+' native gates PASS')
 m.update(status='COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES',finished=time.time(),actual_GH_saving_bytes=sum(v['actual_archive_saving_bytes'] for v in m['candidates']));save('fresh adaptive native archives verified; full/warm/package qualification remains open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
