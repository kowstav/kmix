import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import datetime,hashlib,json,pathlib,shutil,subprocess,time,traceback
import numpy as np
from scipy.special import expit
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');N=R/'atom_cache_v1';S=R/'native_stage_trace_v1';F=R/'native_stage_fit_v2';D=R/'native_stage_weak_confirmation_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','session':355735431,'pid':os.getpid(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'core_retraining':False,'paid_spending_usd':0,'deletions':[],'exports':[],'evaluations':[],'full_native_candidate':False,'scope':'frozen single weak-source head; independent cold C/D Q16 confirmation, not a qualifying archive'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def run(cmd,cwd,env,label):
 t=time.monotonic()
 with (D/(label+'.log')).open('x') as f:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,s,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(s)
 a={'wall_seconds':time.monotonic()-t,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 if p.returncode:m['failed_runtime']=a;raise RuntimeError(label)
 return a
try:
 fm=json.loads((F/'manifest.json').read_text());sm=json.loads((S/'manifest.json').read_text());nm=json.loads((N/'manifest.json').read_text());assert fm['status']=='COMPLETE_NATIVE_STAGE_FINITE_FIT' and len(fm['results'])==31 and all(v['ideal_box_optimum_certified'] and v['supporting_plane_gap_bytes']<=.05 for v in fm['results']);assert fm['future_target_source_role_noninterference']['status']=='PASS';assert 0<fm['best_priced_AB_bytes']<64 and not fm['advance_gate_pass'];best=max(fm['results'],key=lambda v:v['development_after_two_coefficient_copies_and_5bit_selector_bytes']);generic=fm['results'][0];assert best['name']=='neural_valid' and best['arm']==24
 m['frozen_candidate']=best;m['generic_control']=generic;m['fit_manifest_sha256']=sha(F/'manifest.json');m['source_hashes']=[{'file':v,'sha256':sha(R/v)} for v in ['research_round8_native_stage_weak_confirmation_worker.py','research_round8_native_stage_weak_confirmation_protocol.md']];m['production_stream']=nm['production_stream'];save('one candidate frozen before C/D source generation; original64B gate remains failed')
 binary=S/'tree/cmix';weights=P/'lex_audit/lex_h1_run11.tfwc2';dictionary=S/'tree/dictionary/english.dic';assert sha(binary)==sm['binary_sha256'] and sha(weights)==nm['weights_sha256'] and sha(dictionary)==nm['dictionary_sha256'];assert shutil.disk_usage(D).free>800000000
 env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_PREPARE','HP_LEX_'))};env.update(LAB_RAW='1',LAB_VOCAB=str(P/'preserved/data/vocab.bm'),LAB_DICT=str(dictionary),LAB_KEEP_TEMP='1')
 for s in 'cd':
  original=next(v for v in nm['native_exports'] if v['slice']==s);dest=D/(s+'512k');dest.mkdir();(dest/'.dict').symlink_to(dictionary);raw=N/(s+'512k.bin');out=dest/'out.cmx';qp=dest/'final_p.u16';stage=dest/'stage.f32';save('new source observation '+s)
  accounting=run([str(binary),'-n','--transformer',str(weights),str(raw),str(out)],dest,{**env,'LAB_BITTRACE':str(qp),'LAB_STAGETRACE':str(stage)},s+'_source_export')
  assert sha(out)==original['archive_sha256'] and sha(qp)==original['final_p_sha256'] and sha(raw)==original['input_sha256'];assert stage.stat().st_size==318767116 and stage.read_bytes()[:12]==b'HPSTG001\x13\x00\x00\x00'
  ex={'slice':s,'input_sha256':original['input_sha256'],'archive_sha256':sha(out),'native_p_sha256':sha(qp),'stage_sha256':sha(stage),'stage_bytes':stage.stat().st_size,'archive_identity':True,'Q16_identity':True,'accounting':accounting};m['exports'].append(ex);save('unchanged native archive and integer trace '+s+' verified')
  p=np.fromfile(qp,dtype='<u2');source=raw.read_bytes();y=((np.frombuffer(source,np.uint8)[:,None]>>(7-np.arange(8)))&1).astype(np.uint8).reshape(-1);frames=np.memmap(stage,mode='r',dtype='<f4',offset=12,shape=(len(p),19));h=np.memmap(N/(s+'_native/hidden.q8'),mode='r',dtype=np.uint8,shape=(len(source),193));valid=np.repeat(np.r_[np.uint8(0),h[:-1,0]],8).astype(np.float32);assert np.isfinite(frames).all();results=[]
  for head in [best,generic]:
   gain=0.;ideal_gain=0.;predict_sha=hashlib.sha256();theta=np.array(head['coefficients'],np.float64)
   for i in range(0,len(p),131072):
    pp=p[i:i+131072].astype(np.float64);yy=y[i:i+131072].astype(np.float64);ell=np.log(pp/(65536.-pp));X=np.empty((len(pp),len(theta)),np.float64);X[:,0]=1;X[:,1]=ell
    if head is best:
     prob=np.clip(frames[i:i+131072,17].astype(np.float64),1/65536,65535/65536);feature=(np.clip(np.log(prob/(1-prob))-ell,-12,12)/12).astype(np.float32)*valid[i:i+131072];X[:,2]=feature
    z=ell+X@theta;qi=expit(z);q=np.clip(np.floor(qi*65536+.5),1,65535).astype('<u2');base=np.where(yy,pp,65536-pp)/65536.;lik=np.where(yy,q.astype(np.float64),65536.-q)/65536.;gain+=float(np.sum(np.log2(lik/base),dtype=np.float64)/8);ideal_gain+=float(np.sum(np.log2(np.where(yy,qi,1-qi)/base),dtype=np.float64)/8);predict_sha.update(q.tobytes())
   results.append({'name':head['name'],'Q16_saving_bytes':gain,'ideal_saving_bytes':ideal_gain,'Q16_minus_ideal_saving_bytes':gain-ideal_gain,'prediction_sha256':predict_sha.hexdigest()})
  m['evaluations'].append({'slice':s,'bytes':len(source),'results':results,'feature_current_target_not_read':True});save('frozen head and generic independent Q16 scored '+s)
 m['both_slices_improve']=all(v['results'][0]['Q16_saving_bytes']>0 for v in m['evaluations']);m['both_slices_beat_generic']=all(v['results'][0]['Q16_saving_bytes']>v['results'][1]['Q16_saving_bytes'] for v in m['evaluations']);m['candidate_confirmation_gain_bytes']=sum(v['results'][0]['Q16_saving_bytes'] for v in m['evaluations']);m['next_gate']='newly registered actual inline-coder/export/resource test only if both slices improve and beat generic; never extrapolate';m.update(status='COMPLETE_WEAK_SOURCE_INDEPENDENT_Q16_CONFIRMATION',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('independent confirmation complete; no actual candidate archive yet')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved; no duplicate');raise
