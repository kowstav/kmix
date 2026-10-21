import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
import datetime,hashlib,json,pathlib,subprocess,time,traceback
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');D=R/'continuous_strength_v2';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'session':355655943,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'statistical residual fitting with frozen core; finite-family diagnostic only','core_retraining':False,'paid_rental_usd':0,'deletions':[],'results':[]}
def save():(D/'manifest.json').write_text(json.dumps(m,indent=2))
def run(cmd,log):
 with log.open('x') as f:
  start=time.monotonic();p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 account={'wall_seconds':time.monotonic()-start,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 if p.returncode:m['failed_runtime']=account;save();raise RuntimeError((cmd,p.returncode,str(log)))
 return account
def identity_probability(p):return np.maximum(1,np.minimum(65535,np.floor(expit(np.log(p/(65536.-p)))*65536.+.5))).astype(np.int32)
save()
try:
 binary=D/'export';m['compile']=run(['g++','-O3','-std=c++17',str(R/'research_round8_continuous_export.cpp'),'-o',str(binary)],D/'compile.log');m['binary']={'bytes':binary.stat().st_size,'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()};m['sources']=[{'file':f,'sha256':hashlib.sha256((R/f).read_bytes()).hexdigest()} for f in ['research_round8_continuous_export.cpp','research_round8_clean_library.h','research_round8_observer_separated.h','research_round8_continuous_protocol.md']];save()
 args=[str(P/'preserved/gen/.dict'),str(P/'research_round7_remaining_graph.txt'),str(P/'research_round7_remaining_constructors.txt'),str(R/'semantic_graph_v1/semantic_k8.u16')]
 m['parser_selftest_runtime']=run([str(binary),'selftest',*args],D/'selftest.log');m['parser_selftest']=[json.loads(s) for s in (D/'selftest.log').read_text().splitlines()];save()
 dtype=np.dtype([('p','<u2'),('y','u1'),('signals','<f4',(6,))]);assert dtype.itemsize==27;slices=[]
 for s in 'abcd':
  raw=P/'preserved/slices'/(s+'2m.bin') if s in 'ab' else P/(s+'2m.bin');output=D/(s+'.json');account=run([str(binary),str(raw),str(P/'lex_finalbit_2m_v1'/s/'final_p.u16'),*args,'131072',str(output)],D/(s+'.log'));row=json.loads(output.read_text());records=np.fromfile(str(output)+'.features',dtype=dtype);assert len(records)==row['exported_bits'];assert ((records['p']>=1)&(records['y']<=1)).all() and np.isfinite(records['signals']).all();assert np.array_equal(identity_probability(records['p'].astype(np.float64)),records['p']);row.update(slice=s,accounting=account,feature_bytes=pathlib.Path(str(output)+'.features').stat().st_size,feature_sha256=hashlib.sha256(pathlib.Path(str(output)+'.features').read_bytes()).hexdigest());slices.append(records);m.setdefault('exports',[]).append(row);save()
 m['status']='FITTING_CONTINUOUS_HEADS';save();start=time.monotonic();dev=np.concatenate(slices[:2]);pd=dev['p'].astype(np.float64);l=np.log(pd/(65536.-pd));y=dev['y'].astype(np.float64);baseline=np.sum(np.logaddexp(0,l)-y*l,dtype=np.float64);names=['generic','semantic_last_content','shuffled_last_content','spelling_last_content','semantic_topic_context','shuffled_topic_context']
 # Independent derivative/convexity checks on a small synthetic problem.
 rng=np.random.default_rng(814);xx=rng.normal(size=(50,4));ll=rng.normal(size=50);yy=rng.integers(0,2,size=50);tt=rng.uniform(-.5,.5,size=4)
 def toy(t):zz=ll+xx@t;return np.sum(np.logaddexp(0,zz)-yy*zz),xx.T@(expit(zz)-yy)
 ft,gt=toy(tt);eps=1e-5;fd=np.array([(toy(tt+np.eye(4)[j]*eps)[0]-toy(tt-np.eye(4)[j]*eps)[0])/(2*eps) for j in range(4)]);err=float(np.max(np.abs(gt-fd)));assert err<1e-7;qq=expit(ll+xx@tt);h=xx.T@((qq*(1-qq))[:,None]*xx);eigen=float(np.linalg.eigvalsh(h).min());assert eigen>=-1e-10
 grid=np.linspace(-1,1,10001);fgrid=np.array([toy(np.array([a,0,0,0]))[0] for a in grid]);at=np.array([grid[fgrid.argmin()],0,0,0]);fa,ga=toy(at);bound=fa+ga[0]*((-1 if ga[0]>=0 else 1)-at[0]);assert bound<=fgrid.min()+1e-9
 m['independent_selftests']={'gradient_finite_difference_max_error':err,'toy_hessian_min_eigenvalue':eigen,'supporting_plane_grid_check':'PASS','neutral_Q16_all_exports':'PASS'};save()
 for arm,name in enumerate(names):
  if arm==0:X=np.column_stack((np.ones(len(dev)),l))
  else:X=np.column_stack((np.ones(len(dev)),l,dev['signals'][:,arm-1].astype(np.float64),dev['signals'][:,5].astype(np.float64)))
  def fun(t):z=l+X@t;value=np.sum(np.logaddexp(0,z)-y*z,dtype=np.float64);grad=X.T@(expit(z)-y);return value/len(y),grad/len(y)
  best=minimize(fun,np.zeros(X.shape[1]),jac=True,bounds=[(-1,1)]*X.shape[1],method='L-BFGS-B',options={'ftol':1e-16,'gtol':1e-13,'maxiter':500,'maxls':60,'maxcor':20});value,grad=fun(best.x);grad*=len(y);vertex=np.where(grad>=0,-1.,1.);gap=float(grad@(best.x-vertex))/np.log(2)/8;result={'name':name,'coefficients':best.x.tolist(),'coefficient_binary64_bytes':int(8*len(best.x)),'solver_success':bool(best.success),'solver_message':str(best.message),'iterations':int(best.nit),'supporting_plane_gap_bytes':gap,'certified_ideal_development_optimum':bool(gap<=.05),'ideal_development_saving_bytes':float((baseline-value*len(y))/np.log(2)/8),'evaluations':[]}
  for s,records in zip('abcd',slices):
   p=records['p'].astype(np.float64);ell=np.log(p/(65536.-p));yy=records['y'].astype(np.float64);features=np.column_stack((np.ones(len(records)),ell)) if arm==0 else np.column_stack((np.ones(len(records)),ell,records['signals'][:,arm-1].astype(np.float64),records['signals'][:,5].astype(np.float64)));z=ell+features@best.x;qq=np.clip(np.floor(expit(z)*65536+.5),1,65535).astype(np.int32);base=np.where(yy,p,65536-p);actual=np.where(yy,qq,65536-qq);gain=float(np.sum(np.log2(actual/base),dtype=np.float64)/8);idealgain=float(np.sum((np.logaddexp(0,ell)-yy*ell)-(np.logaddexp(0,z)-yy*z),dtype=np.float64)/np.log(2)/8);result['evaluations'].append({'slice':s,'q16_saving_bytes':gain,'ideal_saving_bytes':idealgain,'q16_tax_bytes':idealgain-gain,'prediction_sha256':hashlib.sha256(qq.astype('<u2').tobytes()).hexdigest()})
  result['development_q16_saving_bytes']=sum(v['q16_saving_bytes'] for v in result['evaluations'][:2]);result['confirmation_q16_saving_bytes']=sum(v['q16_saving_bytes'] for v in result['evaluations'][2:]);result['development_after_two_coefficient_copies_and_3bit_selector_bytes']=result['development_q16_saving_bytes']-2*result['coefficient_binary64_bytes']-3/8;m['results'].append(result);save()
 m.update(status='COMPLETE_FINITE_CONTINUOUS_DIAGNOSTIC',fit_evaluate_wall_seconds=time.monotonic()-start,finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
