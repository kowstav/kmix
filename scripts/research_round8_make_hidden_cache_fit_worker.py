
# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
r=project_root(__file__)
old=(project_path('research_round8_continuous_v2_worker.py', base=r)).read_text(encoding='utf-8')
start=old.index('import os');end=old.index('\nsave()\ntry:')
head=old[start:end].replace("D=R/'continuous_strength_v2'", "D=R/'hidden_cache_v1'")
body=r'''
save()
try:
 native=R/'native_hidden_trace_v2';nm=json.loads((native/'manifest.json').read_text());assert nm['status']=='COMPLETE_NATIVE_HIDDEN_IDENTITY_AND_EXPORTS'
 assert all(v['integer_trace_identity'] for v in nm['exports']) and all(v['archive_identity'] and v['hidden_encode_decode_identical'] and v['raw_decode_exact'] for v in nm['controls'])
 m['native_identity_manifest_sha256']=hashlib.sha256((native/'manifest.json').read_bytes()).hexdigest()
 binary=D/'replay';m['compile']=run(['g++','-O3','-march=x86-64-v3','-mrecip=none','-std=c++17',str(R/'research_round8_hidden_cache_replay.cpp'),'-o',str(binary)],D/'compile.log');m['binary']={'bytes':binary.stat().st_size,'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()};m['sources']=[{'file':f,'sha256':hashlib.sha256((R/f).read_bytes()).hexdigest()} for f in ['research_round8_hidden_cache_replay.cpp','research_round8_hidden_cache_protocol.md']]
 m['selftest_runtime']=run([str(binary),'selftest'],D/'selftest.log');m['selftests']=[json.loads(s) for s in (D/'selftest.log').read_text().splitlines()];save()
 dtype=np.dtype([('p','<u2'),('y','u1'),('signals','<f4',(5,))]);assert dtype.itemsize==23;slices=[]
 for s in 'abcd':
  out=D/(s+'.features');account=run([str(binary),str(native/(s+'128k.bin')),str(native/(s+'_128k/final_p.u16')),str(native/(s+'_128k/hidden.q8')),str(out),'131072'],D/(s+'.log'));row=json.loads((D/(s+'.log')).read_text().strip());records=np.fromfile(out,dtype=dtype);assert len(records)==8*131072;assert ((records['p']>=1)&(records['y']<=1)).all() and np.isfinite(records['signals']).all();assert np.array_equal(identity_probability(records['p'].astype(np.float64)),records['p']);row.update(slice=s,accounting=account,feature_sha256=hashlib.sha256(out.read_bytes()).hexdigest());slices.append(records);m.setdefault('exports',[]).append(row);save()
 # Strong future noninterference: change future targets AND hidden keys, and
 # prove all earlier records (including all model features) stay byte-identical.
 raw=bytearray((native/'a128k.bin').read_bytes()[:8192]);hidden=bytearray((native/'a_128k/hidden.q8').read_bytes()[:193*8192]);raw[4096:]=bytes(v^0x5b for v in raw[4096:])
 for i in range(4095,8192):hidden[193*i]=1;hidden[193*i+1:193*(i+1)]=bytes([int(i%256)])*192
 (D/'future_mutated.bin').write_bytes(raw);(D/'future_mutated.q8').write_bytes(hidden);m['noninterference_runtime']=run([str(binary),str(D/'future_mutated.bin'),str(native/'a_128k/final_p.u16'),str(D/'future_mutated.q8'),str(D/'future_mutated.features'),'8192'],D/'noninterference.log');assert (D/'future_mutated.features').read_bytes()[:4096*8*23]==(D/'a.features').read_bytes()[:4096*8*23];m['future_target_and_hidden_noninterference']='PASS';save()
 m['status']='FITTING_CONTINUOUS_HEADS';save();start=time.monotonic();dev=np.concatenate(slices[:2]);pd=dev['p'].astype(np.float64);l=np.log(pd/(65536.-pd));y=dev['y'].astype(np.float64);baseline=np.sum(np.logaddexp(0,l)-y*l,dtype=np.float64)
 names=['generic','hidden192_fifo128','hidden192_fifo512','hidden32_fifo512','shuffled_targets_same_cache','plain_recency_fifo512','joint_hidden_and_recency']
 rng=np.random.default_rng(814);xx=rng.normal(size=(50,4));ll=rng.normal(size=50);yy=rng.integers(0,2,size=50);tt=rng.uniform(-.5,.5,size=4)
 def toy(t):zz=ll+xx@t;return np.sum(np.logaddexp(0,zz)-yy*zz),xx.T@(expit(zz)-yy)
 ft,gt=toy(tt);eps=1e-5;fd=np.array([(toy(tt+np.eye(4)[j]*eps)[0]-toy(tt-np.eye(4)[j]*eps)[0])/(2*eps) for j in range(4)]);err=float(np.max(np.abs(gt-fd)));assert err<1e-7;qq=expit(ll+xx@tt);h=xx.T@((qq*(1-qq))[:,None]*xx);eigen=float(np.linalg.eigvalsh(h).min());assert eigen>=-1e-10;m['independent_selftests']={'gradient_finite_difference_max_error':err,'toy_hessian_min_eigenvalue':eigen,'neutral_Q16_all_exports':'PASS'}
 def feature_matrix(records,arm):
  p=records['p'].astype(np.float64);ell=np.log(p/(65536.-p));cols=[np.ones(len(records)),ell]
  if arm==6:cols.extend(records['signals'][:,j].astype(np.float64) for j in [0,1,2,4])
  elif arm>0:cols.append(records['signals'][:,arm-1].astype(np.float64))
  return np.column_stack(cols)
 for arm,name in enumerate(names):
  X=feature_matrix(dev,arm)
  def fun(t):z=l+X@t;value=np.sum(np.logaddexp(0,z)-y*z,dtype=np.float64);grad=X.T@(expit(z)-y);return value/len(y),grad/len(y)
  best=minimize(fun,np.zeros(X.shape[1]),jac=True,bounds=[(-1,1)]*X.shape[1],method='L-BFGS-B',options={'ftol':1e-16,'gtol':1e-13,'maxiter':500,'maxls':60,'maxcor':20});value,grad=fun(best.x);grad*=len(y);vertex=np.where(grad>=0,-1.,1.);gap=float(grad@(best.x-vertex))/np.log(2)/8
  result={'name':name,'coefficients':best.x.tolist(),'coefficient_binary64_bytes':int(8*len(best.x)),'solver_success':bool(best.success),'iterations':int(best.nit),'supporting_plane_gap_bytes':gap,'certified_ideal_development_optimum':bool(gap<=.05),'evaluations':[]}
  for s,records in zip('abcd',slices):
   p=records['p'].astype(np.float64);ell=np.log(p/(65536.-p));yy=records['y'].astype(np.float64);z=ell+feature_matrix(records,arm)@best.x;qq=np.clip(np.floor(expit(z)*65536+.5),1,65535).astype(np.int32);gain=float(np.sum(np.log2(np.where(yy,qq,65536-qq)/np.where(yy,p,65536-p)),dtype=np.float64)/8);idealgain=float(np.sum((np.logaddexp(0,ell)-yy*ell)-(np.logaddexp(0,z)-yy*z),dtype=np.float64)/np.log(2)/8)
   result['evaluations'].append({'slice':s,'q16_saving_bytes':gain,'ideal_saving_bytes':idealgain,'q16_tax_bytes':idealgain-gain,'prediction_sha256':hashlib.sha256(qq.astype('<u2').tobytes()).hexdigest()})
  result['development_q16_saving_bytes']=sum(v['q16_saving_bytes'] for v in result['evaluations'][:2]);result['confirmation_q16_saving_bytes']=sum(v['q16_saving_bytes'] for v in result['evaluations'][2:]);result['development_after_two_coefficient_copies_and_3bit_selector_bytes']=result['development_q16_saving_bytes']-2*result['coefficient_binary64_bytes']-.375;m['results'].append(result);save();print(json.dumps({'arm':name,'dev_bytes':result['development_q16_saving_bytes'],'confirmation_bytes':result['confirmation_q16_saving_bytes'],'certificate_gap_bytes':gap}),flush=True)
 m.update(status='COMPLETE_NATIVE_HIDDEN_CACHE_DIAGNOSTIC',fit_evaluate_wall_seconds=time.monotonic()-start,finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
'''
(project_path('research_round8_hidden_cache_fit_worker.py', base=r)).write_text(head+body,encoding='utf-8')
print('Generated frozen-core cache replay and bounded fit worker')
