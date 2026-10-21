import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
import datetime,hashlib,json,pathlib,shutil,subprocess,time,traceback
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');D=R/'error_memory_v1';D.mkdir(exist_ok=False)
SIZE=524288;offsets={'a':0,'b':102635191,'c':310000000,'d':520000000}
m={'status':'RUNNING','pid':os.getpid(),'session':355655943,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'canonical lexical paired-error memory; native exports reused; registered conditional confirmation','core_retraining':False,'paid_rental_usd':0,'deletions':[],'results':[],'offsets':offsets,'slice_bytes':SIZE,'confirmation_candidates_evaluated':False,'full_native_candidate':False}
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
try:
 N=R/'atom_cache_v1';deadline=time.monotonic()+7200;save('waiting for existing canonical job; no duplicate native inference')
 while True:
  p=N/'manifest.json';nm=json.loads(p.read_text()) if p.exists() else {}
  if nm.get('status','').startswith('COMPLETE') or nm.get('status')=='FAIL':break
  if time.monotonic()>deadline:raise RuntimeError('Existing canonical job still active after two-hour dependent wait; preserve and inspect, no duplicate')
  time.sleep(30)
 assert len(nm.get('controls',[]))==2 and all(v['archive_identity'] and v['final_Q16_identity'] and v['decoded_raw_exact'] and v['hidden_encode_decode_identity'] for v in nm['controls'])
 assert len(nm.get('native_exports',[]))==4
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
  out=D/(s+'.features');result=D/(s+'.replay.json');account=run([str(replay),str(D/(s+'512k.bin')),str(D/(s+'_native/final_p.u16')),str(D/(s+'_native/hidden.q8')),str(dictionary),str(out),str(SIZE),str(result)],R,env,s+'_replay');records=np.fromfile(out,dtype=dtype);assert len(records)==8*SIZE and np.isfinite(records['signals']).all() and np.all(records['y']<=1) and np.array_equal(identity(records['p'].astype(np.float64)),records['p']);row=json.loads(result.read_text());row.update(slice=s,feature_sha256=sha(out),accounting=account);m['feature_exports'].append(row);data[s]=records;save('paired-error features '+s+' exported');return records
 for s in 'ab':export(s)
 raw=bytearray((D/'a512k.bin').read_bytes()[:8192]);hidden=bytearray((D/'a_native/hidden.q8').read_bytes()[:193*8192]);changed=False
 # A future literal-space substitution preserves encoded-atom boundaries.
 for j in range(4096,8192):
  if raw[j]==32 and raw[j-1]!=12:raw[j]=10;changed=True;break
 assert changed
 for j in range(4095,8192):hidden[193*j]=1;hidden[193*j+1:193*(j+1)]=bytes([j%256])*192
 (D/'future.bin').write_bytes(raw);(D/'future.q8').write_bytes(hidden);m['noninterference_accounting']=run([str(replay),str(D/'future.bin'),str(D/'a_native/final_p.u16'),str(D/'future.q8'),str(dictionary),str(D/'future.features'),'8192',str(D/'future.replay.json')],R,env,'future');assert (D/'future.features').read_bytes()[:4096*8*91]==(D/'a.features').read_bytes()[:4096*8*91];m['future_target_and_hidden_noninterference']='PASS'
 m['status']='FITTING_DEVELOPMENT_ONLY';save('A/B coefficients; C/D candidates untouched')
 dev=np.concatenate([data['a'],data['b']]);pd=dev['p'].astype(np.float64);l=np.log(pd/(65536-pd));y=dev['y'].astype(np.float64)
 sources=[f'{geom}_{control}_lambda{lam}' for geom in ['raw','centered','white'] for control in ['actual','paired_permutation'] for lam in ['025','1','4']]+['prefix_hashed_control','recency_control','raw_actual_one_Newton','raw_permuted_one_Newton'];names=['generic']+sources+['joint']
 def matrix(records,arm):
  p=records['p'].astype(np.float64);cols=[np.ones(len(records)),np.log(p/(65536-p))]
  if arm==23:cols.extend(records['signals'][:,j].astype(np.float64) for j in [1,7,13,18,19,20])
  elif arm:cols.append(records['signals'][:,arm-1].astype(np.float64))
  return np.column_stack(cols)
 rng=np.random.default_rng(18547);xx=rng.normal(size=(51,5));ll=rng.normal(size=51);yy=rng.integers(0,2,size=51);tt=rng.uniform(-1,1,size=5)
 def toy(t):z=ll+xx@t;return np.sum(np.logaddexp(0,z)-yy*z),xx.T@(expit(z)-yy)
 _,g=toy(tt);eps=1e-5;fd=np.array([(toy(tt+np.eye(5)[j]*eps)[0]-toy(tt-np.eye(5)[j]*eps)[0])/(2*eps) for j in range(5)]);err=float(np.max(np.abs(fd-g)));qq=expit(ll+xx@tt);mineig=float(np.linalg.eigvalsh(xx.T@((qq*(1-qq))[:,None]*xx)).min());assert err<1e-7 and mineig>=-1e-10;m['independent_gradient_Hessian_test']={'max_gradient_error':err,'min_Hessian_eigenvalue':mineig}
 def evaluate(records,arm,t):
  p=records['p'].astype(np.float64);ell=np.log(p/(65536-p));yy=records['y'].astype(np.float64);z=ell+matrix(records,arm)@t;q=np.clip(np.floor(expit(z)*65536+.5),1,65535).astype('<u2');gain=float(np.sum(np.log2(np.where(yy,q,65536.-q)/np.where(yy,p,65536.-p)),dtype=np.float64)/8);ideal=float(np.sum(np.logaddexp(0,ell)-yy*ell-np.logaddexp(0,z)+yy*z,dtype=np.float64)/np.log(2)/8);return {'q16_saving_bytes':gain,'ideal_saving_bytes':ideal,'q16_tax_bytes':ideal-gain,'prediction_sha256':hashlib.sha256(q.tobytes()).hexdigest()}
 for arm,name in enumerate(names):
  X=matrix(dev,arm)
  def fun(t):z=l+X@t;return np.mean(np.logaddexp(0,z)-y*z),X.T@(expit(z)-y)/len(y)
  opt=minimize(fun,np.zeros(X.shape[1]),jac=True,bounds=[(-1,1)]*X.shape[1],method='L-BFGS-B',options={'ftol':1e-16,'gtol':1e-13,'maxiter':500,'maxls':60,'maxcor':20});_,grad=fun(opt.x);grad*=len(y);vertex=np.where(grad>=0,-1,1);gap=max(0.,float(grad@(opt.x-vertex))/np.log(2)/8);evaluations=[dict(slice=s,**evaluate(data[s],arm,opt.x)) for s in 'ab'];gain=sum(v['q16_saving_bytes'] for v in evaluations);result={'name':name,'arm':arm,'coefficients':opt.x.tolist(),'coefficient_bytes_per_copy':8*len(opt.x),'supporting_plane_gap_bytes':gap,'ideal_box_optimum_certified':gap<=.05,'solver_success':bool(opt.success),'evaluations':evaluations,'development_q16_saving_bytes':gain,'development_after_two_coefficient_copies_and_5bit_selector_bytes':gain-16*len(opt.x)-.625};m['results'].append(result);save('fit '+name);del X
 assert all(v['ideal_box_optimum_certified'] for v in m['results'])
 fixed={name:sum(v[name] for v in m['feature_exports']) for name in ['bayes_global_saving_bytes','bayes_context_saving_bytes']};m['fixed_online_AB']=fixed;m['advance_gate_bytes']=64.;best=max(m['results'],key=lambda v:v['development_after_two_coefficient_copies_and_5bit_selector_bytes']);m['selected_development_head']=best['name'];m['best_priced_AB_bytes']=best['development_after_two_coefficient_copies_and_5bit_selector_bytes'];advance=max(m['best_priced_AB_bytes'],max(fixed.values()))>=64;m['advance_gate_pass']=advance;save('locked A/B advancement gate')
 del dev,pd,l,y
 if advance:
  # Conditional registered confirmation: no refit or hyperparameter change.
  for s in 'cd':export(s)
  for v in m['results']:v['evaluations'].extend(dict(slice=s,**evaluate(data[s],v['arm'],np.array(v['coefficients']))) for s in 'cd');v['confirmation_q16_saving_bytes']=sum(a['q16_saving_bytes'] for a in v['evaluations'] if a['slice'] in 'cd')
  m['confirmation_candidates_evaluated']=True;m['fixed_online_CD']={name:sum(v[name] for v in m['feature_exports'] if v['slice'] in 'cd') for name in fixed}
 m.update(status='COMPLETE_CANONICAL_ERROR_MEMORY_DIAGNOSTIC',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('finite paired-error branch complete; full warm/native package remains open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved; no duplicate restart');raise
