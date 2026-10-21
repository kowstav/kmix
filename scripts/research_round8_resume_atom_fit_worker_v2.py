import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
import datetime,hashlib,json,pathlib,subprocess,time,traceback
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize
R=pathlib.Path('/kaggle/working/hp_round8');N=R/'atom_cache_v1';D=R/'atom_fit_resume_v2';D.mkdir(exist_ok=False)
SIZE=524288;dtype=np.dtype([('p','<u2'),('y','u1'),('signals','<f4',(9,))]);assert dtype.itemsize==39
m={'status':'RUNNING','pid':os.getpid(),'session':355735431,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'resume interrupted canonical finite fit; original native exports and A/B features reused unchanged','core_retraining':False,'paid_rental_usd':0,'deletions':[],'results':[],'confirmation_candidates_evaluated':False,'full_native_candidate':False,'advance_gate_bytes':64}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2,default=lambda value:value.item() if isinstance(value,np.generic) else str(value)));print(json.dumps({'status':m['status'],'stage':stage}),flush=True)
def run(cmd,cwd,env,label):
 t=time.monotonic()
 with (D/(label+'.log')).open('x') as f:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,s,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(s)
 a={'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'wall_seconds':time.monotonic()-t,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 if p.returncode:m['failed_runtime']=a;save('failure');raise RuntimeError((label,p.returncode))
 return a
names=['generic','raw_word','permuted_raw_word','centered_word','permuted_centered_word','white_word','permuted_white_word','word_recency','centered_hard_word','permuted_centered_hard_word','joint']
def columns(records,arm):
 p=records['p'].astype(np.float64);cols=[np.ones(len(records)),np.log(p/(65536-p))]
 if arm==10:cols.extend(records['signals'][:,j].astype(np.float64) for j in [0,2,4,6,7])
 elif arm:cols.append(records['signals'][:,arm-1].astype(np.float64))
 return np.column_stack(cols)
_prepared_cache={}
_prepared_arm=None
def summation(data,arm,t,hessian=False):
 value=0.;g=np.zeros(len(t));H=np.zeros((len(t),len(t)))
 for rec in data:
  for i in range(0,len(rec),131072):
   a=rec[i:i+131072];X,yy=_prepared_cache[id(rec)];X=X[i:i+131072];l=X[:,1];y=yy[i:i+131072];z=l+X@t;q=expit(z);value+=np.sum(np.logaddexp(0,z)-y*z,dtype=np.float64);g+=X.T@(q-y)
   if hessian:H+=X.T@((q*(1-q))[:,None]*X)
 return value,g,H
def gap(t,g):return float(max(0.,float(g@(t-np.where(g>=0,-1,1)))/np.log(2)/8))
def solve(data,arm):
 global _prepared_cache,_prepared_arm
 _prepared_cache.clear();_prepared_arm=arm
 for rec in data:_prepared_cache[id(rec)]=(columns(rec,arm),rec['y'].astype(np.float64))
 dim=7 if arm==10 else 2 if arm==0 else 3;t=np.zeros(dim);history=[]
 for it in range(40):
  f,g,H=summation(data,arm,t,True);cert=gap(t,g);history.append({'iteration':it,'supporting_plane_gap_bytes':cert})
  if cert<=.005:return t,history,'streamed_active_set_Newton'
  free=~(((t<=-1+1e-12)&(g>=0))|((t>=1-1e-12)&(g<=0)));ix=np.flatnonzero(free)
  if not len(ix):return t,history,'streamed_active_set_Newton'
  step=np.zeros(dim);hh=H[np.ix_(ix,ix)];ridge=max(1e-10,float(np.trace(hh))*1e-12/max(1,len(ix)))
  step[ix]=-np.linalg.solve(hh+ridge*np.eye(len(ix)),g[ix]);accepted=False
  for ls in range(22):
   trial=np.clip(t+step*2.**(-ls),-1,1);direction=trial-t
   if np.max(np.abs(direction))<1e-14:break
   ff,_,_=summation(data,arm,trial)
   if ff<=f+1e-4*float(g@direction):t=trial;accepted=True;break
  if not accepted:break
 # Same convex class; independent optimizer fallback, still certified below.
 def fun(x):f,g,_=summation(data,arm,x);return f/sum(len(a) for a in data),g/sum(len(a) for a in data)
 opt=minimize(fun,t,jac=True,bounds=[(-1,1)]*dim,method='L-BFGS-B',options={'ftol':1e-16,'gtol':1e-13,'maxiter':150,'maxls':50});return opt.x,history,'streamed_Newton_then_LBFGSB'
def evaluate(rec,arm,t):
 gain=ideal=0.;h=hashlib.sha256()
 for i in range(0,len(rec),131072):
  a=rec[i:i+131072];p=a['p'].astype(np.float64);l=np.log(p/(65536-p));y=a['y'].astype(np.float64);z=l+columns(a,arm)@t;q=np.clip(np.floor(expit(z)*65536+.5),1,65535).astype('<u2');gain+=np.sum(np.log2(np.where(y,q,65536.-q)/np.where(y,p,65536.-p)),dtype=np.float64)/8;ideal+=np.sum(np.logaddexp(0,l)-y*l-np.logaddexp(0,z)+y*z,dtype=np.float64)/np.log(2)/8;h.update(q.tobytes())
 return {'q16_saving_bytes':float(gain),'ideal_saving_bytes':float(ideal),'q16_tax_bytes':float(ideal-gain),'prediction_sha256':h.hexdigest()}
try:
 save('validate preserved native/feature hashes; no repeat inference')
 assert not any('/research_round8_atom_cache_worker.py' in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines())
 nm=json.loads((N/'manifest.json').read_text());assert len(nm['controls'])==2 and all(v['archive_identity'] and v['decoded_raw_exact'] and v['hidden_encode_decode_identity'] for v in nm['controls']);assert len(nm['native_exports'])==4 and len(nm['feature_exports'])==2 and nm['future_target_and_hidden_noninterference']=='PASS'
 for v in nm['native_exports']:
  s=v['slice'];assert sha(N/(s+'512k.bin'))==v['input_sha256'] and sha(N/(s+'_native/final_p.u16'))==v['final_p_sha256'] and sha(N/(s+'_native/hidden.q8'))==v['hidden_sha256']
 data={}
 for v in nm['feature_exports']:
  s=v['slice'];assert sha(N/(s+'.features'))==v['feature_sha256'];data[s]=np.memmap(N/(s+'.features'),dtype=dtype,mode='r');assert len(data[s])==SIZE*8
 m['reused_interrupted_manifest_sha256']=sha(N/'manifest.json');m['production_stream']=nm['production_stream'];m['controls']=nm['controls'];m['native_exports']=nm['native_exports'];m['feature_exports']=nm['feature_exports'];m['future_target_and_hidden_noninterference']='PASS';m['selftest']=nm['selftest'];m['native_inference_reused_without_duplicate']=True;m['source_hashes']=nm['source_hashes']+[{'file':pathlib.Path(__file__).name,'sha256':sha(R/pathlib.Path(__file__).name)}]
 rng=np.random.default_rng(941);X=rng.normal(size=(71,7));yy=rng.integers(0,2,size=71);l=rng.normal(size=71);t=rng.uniform(-.4,.4,size=7);z=l+X@t;q=expit(z);g=X.T@(q-yy);H=X.T@((q*(1-q))[:,None]*X);eps=1e-5
 def toy(x):z=l+X@x;return np.sum(np.logaddexp(0,z)-yy*z)
 fd=np.array([(toy(t+np.eye(7)[j]*eps)-toy(t-np.eye(7)[j]*eps))/(2*eps) for j in range(7)]);err=float(np.max(np.abs(fd-g)));mineig=float(np.linalg.eigvalsh(H).min());assert err<1e-7 and mineig>=0;m['independent_math_test']={'gradient_error':err,'Hessian_min_eigenvalue':mineig};save('streamed convex fitting; same registered feature/box family')
 for arm,name in enumerate(names):
  start=time.monotonic();t,hist,solver=solve([data['a'],data['b']],arm);_,g,_=summation([data['a'],data['b']],arm,t);cert=gap(t,g);evals=[dict(slice=s,**evaluate(data[s],arm,t)) for s in 'ab'];gain=sum(v['q16_saving_bytes'] for v in evals);row={'name':name,'arm':arm,'coefficients':t.tolist(),'coefficient_bytes_per_copy':8*len(t),'supporting_plane_gap_bytes':cert,'ideal_box_optimum_certified':cert<=.05,'solver':solver,'iteration_history':hist,'fit_evaluate_wall_seconds':time.monotonic()-start,'evaluations':evals,'development_q16_saving_bytes':gain,'development_after_two_coefficient_copies_and_4bit_selector_bytes':gain-16*len(t)-.5};m['results'].append(row);save('fit '+name);assert cert<=.05
 m['fixed_online_AB']={name:sum(v[name] for v in m['feature_exports']) for name in ['bayes_global_saving_bytes','bayes_context_saving_bytes']};best=max(m['results'],key=lambda v:v['development_after_two_coefficient_copies_and_4bit_selector_bytes']);m['selected_development_head']=best['name'];m['best_priced_AB_bytes']=best['development_after_two_coefficient_copies_and_4bit_selector_bytes'];advance=max(m['best_priced_AB_bytes'],max(m['fixed_online_AB'].values()))>=64;m['advance_gate_pass']=advance;save('locked development advancement gate')
 if advance:
  env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};binary=D/'replay';m['compile']=run(['g++','-O3','-march=x86-64-v3','-mrecip=none','-std=c++17',str(R/'research_round8_atom_cache.cpp'),'-o',str(binary)],R,env,'compile');dictionary=R/'native_hidden_trace_v1/tree/dictionary/english.dic'
  for s in 'cd':
   out=D/(s+'.features');res=D/(s+'.replay.json');account=run([str(binary),str(N/(s+'512k.bin')),str(N/(s+'_native/final_p.u16')),str(N/(s+'_native/hidden.q8')),str(dictionary),str(out),str(SIZE),str(res)],R,env,s+'_replay');data[s]=np.memmap(out,dtype=dtype,mode='r');v=json.loads(res.read_text());v.update(slice=s,feature_sha256=sha(out),accounting=account);m['feature_exports'].append(v)
  for v in m['results']:v['evaluations'].extend(dict(slice=s,**evaluate(data[s],v['arm'],np.array(v['coefficients']))) for s in 'cd');v['confirmation_q16_saving_bytes']=sum(a['q16_saving_bytes'] for a in v['evaluations'] if a['slice'] in 'cd')
  m['confirmation_candidates_evaluated']=True;m['fixed_online_CD']={name:sum(v[name] for v in m['feature_exports'] if v['slice'] in 'cd') for name in m['fixed_online_AB']}
 m.update(status='COMPLETE_CANONICAL_ATOM_CACHE_DIAGNOSTIC',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('resumed finite branch complete; no full native/qualifying result')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved; no duplicate restart');raise
