import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
import datetime,hashlib,json,pathlib,shutil,subprocess,time,traceback
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');D=R/'error_memory_resume_v1';D.mkdir(exist_ok=False)
SIZE=524288;offsets={'a':0,'b':102635191,'c':310000000,'d':520000000}
m={'status':'RUNNING','pid':os.getpid(),'session':355735431,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'canonical lexical paired-error memory; native exports reused; registered conditional confirmation','core_retraining':False,'paid_rental_usd':0,'deletions':[],'results':[],'offsets':offsets,'slice_bytes':SIZE,'confirmation_candidates_evaluated':False,'full_native_candidate':False}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps({'status':m['status'],'stage':stage}),flush=True)
def run(cmd,cwd,env,label):
 t=time.monotonic()
 with (D/(label+'.log')).open('x') as f:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,s,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(s)
 a={'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'wall_seconds':time.monotonic()-t,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 if p.returncode:m['failed_runtime']=a;save('failure');raise RuntimeError((label,p.returncode))
 return a
def identity(p):return np.clip(np.floor(expit(np.log(p/(65536.-p)))*65536+.5),1,65535).astype(np.uint16)
def columns(records,arm):
 p=records['p'].astype(np.float64);cols=[np.ones(len(records)),np.log(p/(65536-p))]
 if arm==23:cols.extend(records['signals'][:,j].astype(np.float64) for j in [1,7,13,18,19,20])
 elif arm:cols.append(records['signals'][:,arm-1].astype(np.float64))
 return np.column_stack(cols)
def summation(data,arm,t,hessian=False):
 value=0.;g=np.zeros(len(t));H=np.zeros((len(t),len(t)))
 for rec in data:
  for i in range(0,len(rec),131072):
   a=rec[i:i+131072];X=columns(a,arm);l=X[:,1];y=a['y'].astype(np.float64);z=l+X@t;q=expit(z);value+=np.sum(np.logaddexp(0,z)-y*z,dtype=np.float64);g+=X.T@(q-y)
   if hessian:H+=X.T@((q*(1-q))[:,None]*X)
 return value,g,H
def gap(t,g):return max(0.,float(g@(t-np.where(g>=0,-1,1)))/np.log(2)/8)
def solve(data,arm):
 dim=8 if arm==23 else 2 if arm==0 else 3;t=np.zeros(dim);history=[]
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
 N=R/'atom_cache_v1';deadline=time.monotonic()+7200;save('waiting for existing canonical job; no duplicate native inference')
 while True:
  p=R/'atom_fit_resume_v1/manifest.json';parent=json.loads(p.read_text()) if p.exists() else {};nm=json.loads((N/'manifest.json').read_text())
  if parent.get('status','').startswith('COMPLETE') or parent.get('status')=='FAIL':break
  if time.monotonic()>deadline:raise RuntimeError('Existing canonical job still active after two-hour dependent wait; preserve and inspect, no duplicate')
  time.sleep(30)
 assert len(nm.get('controls',[]))==2 and all(v['archive_identity'] and v['final_Q16_identity'] and v['decoded_raw_exact'] and v['hidden_encode_decode_identity'] for v in nm['controls'])
 assert len(nm.get('native_exports',[]))==4
 m['parent_fit_status']=parent['status'];m['parent_fit_manifest_sha256']=sha(p)

 for v in nm['native_exports']:
  s=v['slice'];assert sha(N/(s+'512k.bin'))==v['input_sha256'] and sha(N/(s+'_native/final_p.u16'))==v['final_p_sha256'] and sha(N/(s+'_native/hidden.q8'))==v['hidden_sha256']
 m['reused_native_manifest_sha256']=sha(N/'manifest.json');m['reused_native_status']=nm['status'];m['production_stream']=nm['production_stream'];m['controls']=nm['controls'];m['native_exports']=nm['native_exports'];m['native_inference_reused_without_duplicate']=True
 dictionary=R/'native_hidden_trace_v1/tree/dictionary/english.dic';assert sha(dictionary)==nm['dictionary_sha256']
 env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','HP_LEX_','FX_PREPARE'))}
 for s in 'abcd':
  (D/(s+'512k.bin')).symlink_to(N/(s+'512k.bin'));(D/(s+'_native')).symlink_to(N/(s+'_native'))
 assert shutil.disk_usage(R).free>1_600_000_000
 save('reused canonical native controls PASS; independent error-memory replay')
 replay=D/'replay';m['compile']=run(['g++','-O3','-march=x86-64-v3','-mrecip=none','-std=c++17',str(R/'research_round8_error_memory.cpp'),'-o',str(replay)],R,env,'compile');m['replay_binary']={'bytes':replay.stat().st_size,'sha256':sha(replay)};m['source_hashes']=[{'file':n,'sha256':sha(R/n)} for n in ['research_round8_error_memory.cpp','research_round8_atom_cache.cpp','research_round8_residual_memory_math.md',pathlib.Path(__file__).name]];m['selftest_accounting']=run([str(replay),'selftest'],R,env,'selftest');m['selftest']=json.loads((D/'selftest.log').read_text());save('atom probability/geometry selftests PASS')
 dtype=np.dtype([('p','<u2'),('y','u1'),('signals','<f4',(22,))]);assert dtype.itemsize==91;m['feature_exports']=[];data={}
 def export(s):
  out=D/(s+'.features');result=D/(s+'.replay.json');account=run([str(replay),str(D/(s+'512k.bin')),str(D/(s+'_native/final_p.u16')),str(D/(s+'_native/hidden.q8')),str(dictionary),str(out),str(SIZE),str(result)],R,env,s+'_replay');records=np.memmap(out,dtype=dtype,mode='r');assert len(records)==8*SIZE and np.isfinite(records['signals']).all() and np.all(records['y']<=1) and np.array_equal(identity(records['p'].astype(np.float64)),records['p']);row=json.loads(result.read_text());row.update(slice=s,feature_sha256=sha(out),accounting=account);m['feature_exports'].append(row);data[s]=records;save('paired-error features '+s+' exported');return records
 for s in 'ab':export(s)
 raw=bytearray((D/'a512k.bin').read_bytes()[:8192]);hidden=bytearray((D/'a_native/hidden.q8').read_bytes()[:193*8192]);changed=False
 # A future literal-space substitution preserves encoded-atom boundaries.
 for j in range(4096,8192):
  if raw[j]==32 and raw[j-1]!=12:raw[j]=10;changed=True;break
 assert changed
 for j in range(4095,8192):hidden[193*j]=1;hidden[193*j+1:193*(j+1)]=bytes([j%256])*192
 (D/'future.bin').write_bytes(raw);(D/'future.q8').write_bytes(hidden);m['noninterference_accounting']=run([str(replay),str(D/'future.bin'),str(D/'a_native/final_p.u16'),str(D/'future.q8'),str(dictionary),str(D/'future.features'),'8192',str(D/'future.replay.json')],R,env,'future');assert (D/'future.features').read_bytes()[:4096*8*91]==(D/'a.features').read_bytes()[:4096*8*91];m['future_target_and_hidden_noninterference']='PASS'

 m['status']='FITTING_DEVELOPMENT_ONLY';save('streamed bounded A/B fitting; conditional C/D untouched')
 sources=[f'{geom}_{control}_lambda{lam}' for geom in ['raw','centered','white'] for control in ['actual','paired_permutation'] for lam in ['025','1','4']]+['prefix_hashed_control','recency_control','raw_actual_one_Newton','raw_permuted_one_Newton'];names=['generic']+sources+['joint']
 rng=np.random.default_rng(18547);X=rng.normal(size=(71,8));yy=rng.integers(0,2,size=71);l=rng.normal(size=71);t=rng.uniform(-.4,.4,size=8);z=l+X@t;q=expit(z);g=X.T@(q-yy);H=X.T@((q*(1-q))[:,None]*X);eps=1e-5
 def toy(x):z=l+X@x;return np.sum(np.logaddexp(0,z)-yy*z)
 fd=np.array([(toy(t+np.eye(8)[j]*eps)-toy(t-np.eye(8)[j]*eps))/(2*eps) for j in range(8)]);err=float(np.max(np.abs(fd-g)));mineig=float(np.linalg.eigvalsh(H).min());assert err<1e-7 and mineig>=0;m['independent_math_test']={'gradient_error':err,'Hessian_min_eigenvalue':mineig}
 for arm,name in enumerate(names):
  begin=time.monotonic();t,hist,solver=solve([data['a'],data['b']],arm);_,g,_=summation([data['a'],data['b']],arm,t);cert=gap(t,g);evals=[dict(slice=s,**evaluate(data[s],arm,t)) for s in 'ab'];gain=sum(v['q16_saving_bytes'] for v in evals);row={'name':name,'arm':arm,'coefficients':t.tolist(),'coefficient_bytes_per_copy':8*len(t),'supporting_plane_gap_bytes':cert,'ideal_box_optimum_certified':cert<=.05,'solver':solver,'iteration_history':hist,'fit_evaluate_wall_seconds':time.monotonic()-begin,'evaluations':evals,'development_q16_saving_bytes':gain,'development_after_two_coefficient_copies_and_5bit_selector_bytes':gain-16*len(t)-.625};m['results'].append(row);save('fit '+name);assert cert<=.05
 fixed={name:sum(v[name] for v in m['feature_exports']) for name in ['bayes_global_saving_bytes','bayes_context_saving_bytes']};m['fixed_online_AB']=fixed;m['advance_gate_bytes']=64.;best=max(m['results'],key=lambda v:v['development_after_two_coefficient_copies_and_5bit_selector_bytes']);m['selected_development_head']=best['name'];m['best_priced_AB_bytes']=best['development_after_two_coefficient_copies_and_5bit_selector_bytes'];advance=max(m['best_priced_AB_bytes'],max(fixed.values()))>=64;m['advance_gate_pass']=advance;save('locked A/B advancement gate')
 if advance:
  for s in 'cd':export(s)
  for v in m['results']:v['evaluations'].extend(dict(slice=s,**evaluate(data[s],v['arm'],np.array(v['coefficients']))) for s in 'cd');v['confirmation_q16_saving_bytes']=sum(a['q16_saving_bytes'] for a in v['evaluations'] if a['slice'] in 'cd')
  m['confirmation_candidates_evaluated']=True;m['fixed_online_CD']={name:sum(v[name] for v in m['feature_exports'] if v['slice'] in 'cd') for name in fixed}
 m.update(status='COMPLETE_CANONICAL_ERROR_MEMORY_DIAGNOSTIC',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('finite paired-error branch complete; full warm/native package remains open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved; no duplicate restart');raise
