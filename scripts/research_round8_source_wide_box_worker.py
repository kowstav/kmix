import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import datetime,hashlib,json,pathlib,time,traceback
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize
R=pathlib.Path('/kaggle/working/hp_round8');N=R/'atom_cache_v1';S=R/'native_stage_trace_v1';D=R/'source_wide_box_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','session':355735431,'pid':os.getpid(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'core_retraining':False,'paid_spending_usd':0,'deletions':[],'new_confirmation_evaluated':False}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def save(s):m['stage']=s;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(s,flush=True)
lo=np.array([-1.,-1.,-12.]);hi=np.array([1.,1.,12.]);data=[]
def objective(t,hessian=False):
 total=0.;g=np.zeros(3);H=np.zeros((3,3))
 for p,y,feature in data:
  for i in range(0,len(p),131072):
   pp=p[i:i+131072].astype(np.float64);ell=np.log(pp/(65536.-pp));X=np.column_stack([np.ones(len(pp)),ell,feature[i:i+131072]]);yy=y[i:i+131072];z=ell+X@t;q=expit(z);total+=float(np.sum(np.logaddexp(0,z)-yy*z));g+=X.T@(q-yy)
   if hessian:H+=X.T@((q*(1-q))[:,None]*X)
 return total,g,H
def certificate(t,g):return max(0.,float(g@(t-np.where(g>=0,lo,hi)))/np.log(2)/8)
try:
 old=json.loads((R/'native_stage_fit_v2/manifest.json').read_text());assert old['status']=='COMPLETE_NATIVE_STAGE_FINITE_FIT';narrow=old['results'][24];assert narrow['name']=='neural_valid' and narrow['coefficients'][2]==1;nm=json.loads((N/'manifest.json').read_text());sm=json.loads((S/'manifest.json').read_text());m['narrow_fit_manifest_sha256']=sha(R/'native_stage_fit_v2/manifest.json');m['source_hashes']=[{'file':v,'sha256':sha(R/v)} for v in ['research_round8_source_wide_box_worker.py','research_round8_source_wide_box_protocol.md']];m['production_stream']=nm['production_stream'];m['feature_provenance']=[];save('assembling unchanged original feature, no C/D or new E/F read')
 for s in 'ab':
  ref=next(v for v in nm['native_exports'] if v['slice']==s);ex=next(v for v in sm['exports'] if v['slice']==s);pp=N/(s+'_native/final_p.u16');hp=N/(s+'_native/hidden.q8');sp=S/(s+'512k/stage.f32');assert sha(pp)==ref['final_p_sha256'] and sha(hp)==ref['hidden_sha256'] and sha(sp)==ex['stage_sha256'];raw=(N/(s+'512k.bin')).read_bytes();assert hashlib.sha256(raw).hexdigest()==ref['input_sha256'];p=np.fromfile(pp,dtype='<u2');y=((np.frombuffer(raw,np.uint8)[:,None]>>(7-np.arange(8)))&1).astype(np.float64).reshape(-1);frames=np.memmap(sp,mode='r',dtype='<f4',offset=12,shape=(len(p),19));h=np.memmap(hp,mode='r',dtype=np.uint8,shape=(len(raw),193));valid=np.repeat(np.r_[np.uint8(0),h[:-1,0]],8).astype(np.float32);ell=np.log(p.astype(np.float64)/(65536.-p));prob=np.clip(frames[:,17].astype(np.float64),1/65536,65535/65536);feature=(np.clip(np.log(prob/(1-prob))-ell,-12,12)/12).astype(np.float32)*valid;data.append((p,y,feature));m['feature_provenance'].append({'slice':s,'native_p_sha256':ref['final_p_sha256'],'hidden_sha256':ref['hidden_sha256'],'stage_sha256':ex['stage_sha256'],'original_feature_sha256':hashlib.sha256(feature.tobytes()).hexdigest()})
 start=time.monotonic();narrow_t=np.array(narrow['coefficients']);nf,ng,nH=objective(narrow_t,True);m['active_upper_bound_source_gradient_nats']=float(ng[2]);m['narrow_gradient']=ng.tolist();m['narrow_Hessian']=nH.tolist();t=narrow_t.copy();history=[]
 for it in range(40):
  f,g,H=objective(t,True);gap=certificate(t,g);history.append({'iteration':it,'gap_bytes':gap,'coefficients':t.tolist()})
  if gap<=.005:break
  free=~(((t<=lo+1e-12)&(g>=0))|((t>=hi-1e-12)&(g<=0)));ix=np.flatnonzero(free);step=np.zeros(3);step[ix]=-np.linalg.solve(H[np.ix_(ix,ix)]+np.eye(len(ix))*1e-10,g[ix]);accepted=False
  for ls in range(25):
   trial=np.clip(t+step*2.**(-ls),lo,hi);ff,_,_=objective(trial)
   if ff<=f+1e-4*float(g@(trial-t)):t=trial;accepted=True;break
  if not accepted:break
 f,g,H=objective(t,True)
 if certificate(t,g)>.005:
  def fun(x):f,g,_=objective(x);return f/8388608,g/8388608
  o=minimize(fun,t,jac=True,bounds=list(zip(lo,hi)),method='L-BFGS-B',options={'ftol':1e-16,'gtol':1e-13,'maxiter':150,'maxls':50});t=o.x;f,g,H=objective(t,True)
 cert=certificate(t,g);assert cert<=.05 and f<=nf+1e-7;m['coefficients']=t.tolist();m['bounds']={'lower':lo.tolist(),'upper':hi.tolist()};m['certificate_bytes']=cert;m['ideal_box_optimum_certified']=True;m['history']=history;m['ideal_increment_over_narrow_bytes']=(nf-f)/np.log(2)/8;evals=[]
 for s,(p,y,feature) in zip('ab',data):
  gain=ideal=0.;newsha=hashlib.sha256();oldsha=hashlib.sha256()
  for i in range(0,len(p),131072):
   pp=p[i:i+131072].astype(np.float64);yy=y[i:i+131072];ell=np.log(pp/(65536.-pp));X=np.column_stack([np.ones(len(pp)),ell,feature[i:i+131072]]);q=expit(ell+X@t);u=np.clip(np.floor(q*65536+.5),1,65535).astype('<u2');nq=np.clip(np.floor(expit(ell+X@narrow_t)*65536+.5),1,65535).astype('<u2');oldsha.update(nq.tobytes());newsha.update(u.tobytes());base=np.where(yy,pp,65536-pp)/65536.;gain+=float(np.sum(np.log2(np.where(yy,u.astype(np.float64),65536.-u)/65536./base))/8);ideal+=float(np.sum(np.log2(np.where(yy,q,1-q)/base))/8)
  assert oldsha.hexdigest()==next(v for v in narrow['evaluations'] if v['slice']==s)['prediction_sha256'];evals.append({'slice':s,'Q16_saving_bytes':gain,'ideal_saving_bytes':ideal,'prediction_sha256':newsha.hexdigest(),'old_feature_and_Q16_identity':True})
 total=sum(v['Q16_saving_bytes'] for v in evals);m.update(evaluations=evals,development_Q16_saving_bytes=total,development_after_two_coefficient_copies_and_6bit_selector_bytes=total-48-.75,advance_gate_pass=total-48-.75>=64,fit_wall_seconds=time.monotonic()-start,status='COMPLETE_WIDER_SOURCE_FINITE_BOX',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('wider finite optimum and Q16 scored; new E/F remains untouched')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
