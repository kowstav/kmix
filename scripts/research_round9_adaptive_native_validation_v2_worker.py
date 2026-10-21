"""Fix the reference dtype only; reuse unchanged native binary and G encode.

The registered source-replay worker uses NumPy float64 coefficients. The first
native validator used Python weak scalars on float32 features, rounding one term
prematurely. Explicit float64 features restore the registered law. No coefficient
or policy is refit, and H remains untouched until this corrected validation.
"""
import pathlib,json,os,sys,time,hashlib,traceback,subprocess,ast,math
import numpy as np
from scipy.special import expit
from numba import njit
R=pathlib.Path('/kaggle/working/hp_round8');OUT=pathlib.Path('/kaggle/working/hp_round9');D=OUT/'adaptive_native_v2';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/adaptive_native_v2');S.mkdir(exist_ok=False);OLD=pathlib.Path('/root/hp_round9/adaptive_native_v1');T=OLD/'tree'
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scope':'correct registered float64 reference, reused G native encode, fresh H encode and exact independent decoding','spending_usd':0,'deletions':[],'controls':[],'candidates':[],'scratch':str(S),'offsets':{'g':65000000,'h':375000000},'full_package_qualified':False}
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
try:
 old=json.loads((OUT/'adaptive_native_v1/manifest.json').read_text());selected=json.loads((OUT/'adaptive_source_v1/manifest.json').read_text());assert old['status']=='FAIL' and selected['status']=='COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY'
 m['frozen_policy']=selected['frozen_policy_before_confirmation'];m['binary']=old['binary'];m['controls']=old['controls'];assert len(m['controls'])==1 and m['controls'][0]['independent_decode_exact']
 m['reference_repair']={'dtype':'explicit FP64 multiplication of the stored FP32 feature; restores original source worker NumPy-FP64 coefficient law','previous_reference_failure_preserved':'adaptive_native_v1','native_binary_unchanged':True,'G_teacher_and_candidate_reused':True,'refit':False,'worker_sha256':sha(OUT/'research_round9_adaptive_native_validation_v2_worker.py')}
 binary=T/'cmix';assert sha(binary)==m['binary']['sha256'];teacher=R/'native_stage_trace_v1/tree/cmix';weights=pathlib.Path('/kaggle/working/hp_round7/lex_audit/lex_h1_run11.tfwc2');dictionary=T/'dictionary/english.dic';base={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_PREPARE','HP_LEX_'))};base.update(LAB_RAW='1',LAB_VOCAB='/kaggle/working/hp_round7/preserved/data/vocab.bm',LAB_DICT=str(dictionary),LAB_KEEP_TEMP='1')
 nodes=ast.parse((OUT/'research_round9_adaptive_source_worker.py').read_text());functions=[n for n in nodes.body if isinstance(n,ast.FunctionDef) and n.name=='replay'];ns={'np':np,'math':math,'njit':njit};exec(compile(ast.Module(body=functions,type_ignores=[]),'<frozen-replay>','exec'),ns);replay=ns['replay']
 def decode(raw,out,label,qp,hp):
  dd=S/(label+'_decode');dd.mkdir();(dd/'.dict').symlink_to(dictionary);dq=dd/'final_p.u16';dh=dd/'hidden.q8';a=run([str(binary),'-d','--transformer',str(weights),str(out),'decoded.bin'],dd,{**base,'LAB_DECODE_BITTRACE':str(dq),'LAB_HIDDENTRACE':str(dh)},label+'_decode');assert sha(dd/'decoded.bin')==sha(raw);assert sha(dq)==sha(qp) and sha(dh)==sha(hp);return a
 stream=R/'lexical_full_prepare_v1/lexical_full_ready.wrt'
 for s,offset in m['offsets'].items():
  if s=='g':
   td=OLD/'g_teacher';cd=OLD/'g_candidate';raw=td/'input.bin';tp=td/'final_p.u16';th=td/'hidden.q8';stage=td/'stage.f32';tout=td/'out.cmx';out=cd/'out.cmx';qp=cd/'final_p.u16';hp=cd/'hidden.q8'
   with stream.open('rb') as f:f.seek(offset);assert f.read(524288)==raw.read_bytes()
   ta=ea={'reused_existing_completed_native_run':True,'accounting_logs':str(OUT/'adaptive_native_v1')}
  else:
   td=S/(s+'_teacher');td.mkdir();(td/'.dict').symlink_to(dictionary)
   with stream.open('rb') as f:f.seek(offset);data=f.read(524288)
   raw=td/'input.bin';raw.write_bytes(data);tp=td/'final_p.u16';th=td/'hidden.q8';stage=td/'stage.f32';tout=td/'out.cmx';save('fresh H native teacher observation')
   ta=run([str(teacher),'-n','--transformer',str(weights),str(raw),str(tout)],td,{**base,'LAB_BITTRACE':str(tp),'LAB_HIDDENTRACE':str(th),'LAB_STAGETRACE':str(stage)},s+'_teacher')
   cd=S/(s+'_candidate');cd.mkdir();(cd/'.dict').symlink_to(dictionary);out=cd/'out.cmx';qp=cd/'final_p.u16';hp=cd/'hidden.q8'
  data=raw.read_bytes();p=np.fromfile(tp,'<u2');ell=np.log(p.astype(np.float64)/(65536-p.astype(np.float64)));hidden=np.memmap(th,'u1','r',shape=(len(data),193));valid=np.repeat(np.r_[0,hidden[:-1,0]],8);st=np.memmap(stage,'<f4','r',offset=12,shape=(len(p),19));nn=np.clip(st[:,17].astype(np.float64),1/65536,65535/65536);feat=((np.clip(np.log(nn/(1-nn))-ell,-12,12)/12).astype(np.float32)*valid).astype(np.float64)
  theta=np.array([.0016181118716570748,-.007454085408717222,2.3818512619982752],dtype=np.float64);dot=theta[0]+theta[1]*ell+theta[2]*feat;ex=np.column_stack([p,*[np.clip(np.floor(65536*expit(ell+a*dot)+.5),1,65535).astype('<u2') for a in [.5,1.,1.5,2.]]]);y=((np.frombuffer(data,'u1')[:,None]>>(7-np.arange(8)))&1).reshape(-1);q,ideal,rounded,like=replay(ex,y,2.6441431586476938e-06);expected=hashlib.sha256(q.tobytes()).hexdigest()
  if s=='h':save('fresh H actual adaptive encode');ea=run([str(binary),'-n','--transformer',str(weights),str(raw),str(out)],cd,{**base,'LAB_BITTRACE':str(qp),'LAB_HIDDENTRACE':str(hp)},s+'_candidate_encode')
  assert sha(qp)==expected,(s,'native replay Q16 mismatch');assert sha(hp)==sha(th),(s,'core trajectory changed');save(s+' exact corrected-reference Q16 and unchanged core PASS; independent decoding');da=decode(raw,out,s+'_candidate',qp,hp)
  row={'slice':s,'offset':offset,'input_sha256':sha(raw),'teacher_archive_bytes':tout.stat().st_size,'candidate_archive_bytes':out.stat().st_size,'actual_archive_saving_bytes':tout.stat().st_size-out.stat().st_size,'candidate_archive_sha256':sha(out),'native_Q16_matches_frozen_replay':True,'core_hidden_identity':True,'independent_decode_exact':True,'encode_decode_Q16_hidden_identity':True,'teacher_accounting':ta,'candidate_encode_accounting':ea,'candidate_decode_accounting':da,'rounding_tax_bits':rounded-ideal,'candidate_Q16_sha256':sha(qp)};m['candidates'].append(row);save('all '+s+' native gates PASS')
 m.update(status='COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES',finished=time.time(),actual_GH_saving_bytes=sum(v['actual_archive_saving_bytes'] for v in m['candidates']));save('actual G/H adaptive archives verified; full/warm/package qualification remains open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
