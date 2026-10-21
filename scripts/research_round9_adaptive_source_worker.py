"""No-retraining causal finite-expert Bayesian/fixed-share source correction."""
import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import pathlib,json,time,traceback,hashlib,math
import numpy as np
from numba import njit
from scipy.special import expit,logsumexp
R=pathlib.Path('/kaggle/working/hp_round8');OUT=pathlib.Path('/kaggle/working/hp_round9');D=OUT/'adaptive_source_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scope':'causal Bayesian experts over actual native integer laws, no neural retraining','spending_usd':0,'deletions':[],'development':[],'confirmation':[]}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
@njit
def replay(experts,y,eps):
 K=experts.shape[1];w=np.full(K,1./K);out=np.empty(len(y),np.uint16);ideal=rounded=0.;loglike=np.zeros(K)
 for t in range(len(y)):
  pred=0.
  for k in range(K):pred+=w[k]*experts[t,k]/65536.
  q=min(65535,max(1,int(math.floor(pred*65536+.5))));out[t]=q;py=pred if y[t] else 1.-pred;actual=q/65536. if y[t] else 1.-q/65536.;ideal-=math.log2(py);rounded-=math.log2(actual);total=0.
  for k in range(K):
   pk=experts[t,k]/65536. if y[t] else 1.-experts[t,k]/65536.;w[k]*=pk;total+=w[k];loglike[k]+=math.log2(pk)
  for k in range(K):w[k]=(1.-eps)*w[k]/total+eps/K
 return out,ideal,rounded,loglike
def load(s):
 N=R/'atom_cache_v1';sr=R/'native_stage_trace_v1' if s in 'ab' else R/'native_stage_weak_confirmation_v1' if s in 'cd' else R/'source_wide_confirmation_v1';root=sr/(s+'512k');rawpath=N/(s+'512k.bin') if s in 'abcd' else root/'input.bin';raw=np.frombuffer(rawpath.read_bytes(),'u1');pp=N/(s+'_native/final_p.u16') if s in 'abcd' else root/'final_p.u16';p=np.fromfile(pp,'<u2');ell=np.log(p.astype(np.float64)/(65536-p.astype(np.float64)));hp=N/(s+'_native/hidden.q8') if s in 'abcd' else root/'hidden.q8';h=np.memmap(hp,'u1','r',shape=(len(raw),193));valid=np.repeat(np.r_[0,h[:-1,0]],8);st=np.memmap(root/'stage.f32','<f4','r',offset=12,shape=(len(p),19));nn=np.clip(st[:,17].astype(np.float64),1/65536,65535/65536);f=(np.clip(np.log(nn/(1-nn))-ell,-12,12)/12).astype(np.float32)*valid;theta=np.array(json.loads((R/'source_wide_box_v1/manifest.json').read_text())['coefficients']);delta=theta[0]+theta[1]*ell+theta[2]*f;y=((raw[:,None]>>(7-np.arange(8)))&1).reshape(-1).astype(np.uint8);q=np.clip(np.floor(65536*expit(ell+delta)+.5),1,65535).astype('<u2');families={'two':np.column_stack([p,q]),'scaled5':np.column_stack([p,*[np.clip(np.floor(65536*expit(ell+mult*delta)+.5),1,65535).astype('<u2') for mult in [.5,1.,1.5,2.]]])};return p,q,y,families
def evaluate(p,wide,y,expert,eps):
 t=time.monotonic();q,ideal,rounded,likelihood=replay(expert,y,eps);nativecost=-np.log2(np.where(y,p.astype(np.float64),65536-p.astype(np.float64))/65536).sum();widecost=-np.log2(np.where(y,wide.astype(np.float64),65536-wide.astype(np.float64))/65536).sum();marginal=-logsumexp(likelihood*math.log(2)-math.log(expert.shape[1]))/math.log(2);identity_error=abs(ideal-marginal) if eps==0 else None
 if eps==0:assert identity_error<1e-5,(identity_error,ideal,marginal)
 return {'gain_vs_native_bytes':float((nativecost-rounded)/8),'gain_vs_wide_bytes':float((widecost-rounded)/8),'rounding_tax_bits':float(rounded-ideal),'ideal_regret_vs_best_expert_bits':float(ideal+np.max(likelihood)),'zero_forgetting_marginal_identity_error_bits':identity_error,'probability_sha256':hashlib.sha256(q.tobytes()).hexdigest(),'CPU_wall_seconds':time.monotonic()-t}
try:
 m['worker_sha256']=hashlib.sha256((OUT/'research_round9_adaptive_source_worker.py').read_bytes()).hexdigest();policies=[{'family':fam,'H_bits':h,'eps':0. if h is None else 1-2**(-1/h)} for fam in ['two','scaled5'] for h in [None,1024,16384,262144]];m['policy_definitions']=policies;m['contract']={'expert_update':'after observed bit using integer expert outcome probabilities, fixed-order FP64 posterior then fixed-share','state_reset':'only start of cold slice; no future boundary/oracle routing','price':'policy selector3bits, coefficients24B/copy for scaled5 law; native executable delta unmeasured','development':'A/B, confirmation C/D/E/F viewed by other branches; fit-held-out only','finite_family':'8 policies; not an optimum for all memory/TTL laws'};save('checking finite-expert sequence identity and future-target noninterference')
 ex=np.array([[1,65535],[65535,1],[32768,12345],[17,1234]],np.uint16);y=np.array([1,0,1,0],np.uint8);a=replay(ex,y,0.)[0];b=replay(ex,np.array([1,0,0,1],np.uint8),0.)[0];assert np.array_equal(a[:3],b[:3]);c=ex.copy();c[3]=1;assert np.array_equal(a[:3],replay(c,y,0.)[0][:3]);m['future_target_and_expert_prefix_noninterference']='PASS'
 for s in 'ab':
  p,w,y,fams=load(s)
  for policy in policies:m['development'].append({'slice':s,'policy':policy,'result':evaluate(p,w,y,fams[policy['family']],policy['eps'])});save('development '+s)
 rank=sorted(policies,key=lambda p:sum(v['result']['gain_vs_wide_bytes'] for v in m['development'] if v['policy']==p),reverse=True);m['frozen_policy_before_confirmation']=rank[0];save('best development policy frozen; independent-fit confirmation starts')
 for s in 'cdef':
  p,w,y,fams=load(s);policy=rank[0];m['confirmation'].append({'slice':s,'policy':policy,'result':evaluate(p,w,y,fams[policy['family']],policy['eps'])});save('confirmation '+s)
 m.update(status='COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY',finished=time.time(),native_integration=False,all96_exhausted=False);save('adaptive replay complete; actual native coder qualification remains open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
