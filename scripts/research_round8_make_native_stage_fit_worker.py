
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
old=project_path('research_round8_resume_atom_fit_worker_v2.py').read_text()
helpers=old[old.index('_prepared_cache={}'):old.index('\ntry:')]
helpers=helpers.replace("a['y'].astype(np.float64)","a['y'].astype(np.float64)")
helpers=helpers.replace("dim=7 if arm==10 else 2 if arm==0 else 3;", "dim=2+len(arms[arm]);")
prelude='''import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
import datetime,hashlib,json,pathlib,subprocess,time,traceback,re
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize
R=pathlib.Path('/kaggle/working/hp_round8');N=R/'atom_cache_v1';S=R/'native_stage_trace_v1';D=R/'native_stage_fit_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'session':355735431,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'core_retraining':False,'paid_spending_usd':0,'deletions':[],'results':[],'advance_gate_bytes':64,'confirmation_evaluated':False,'full_native_candidate':False}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2,default=lambda v:v.item()));print(stage,flush=True)
names=['generic']+['raw_source_%02d'%j for j in range(14)]+['preSSE_difference','FXCM_difference','neural_difference','raw_joint','three_difference_joint','raw_plus_difference_joint','delayed_raw_joint','interaction_joint','neural_conflict','neural_valid','neural_FXCM_conflict_valid_joint','role_only','role_difference_joint','role_raw_joint','role_interaction_joint','delayed_role_only']
arms=[[]]+[[j] for j in range(14)]+[[14],[15],[16],list(range(14)),[14,15,16],list(range(17)),list(range(23,37)),[14,15,16,17,18,19,20],[18],[17],[15,16,18,17],list(range(37,43)),list(range(37,43))+[14,15,16],list(range(37,43))+list(range(14)),list(range(37,43))+[14,15,16,17,18,19,20],list(range(43,49))]
assert len(arms)==len(names)==31
class Records:
 def __init__(self,p,y,signals):self.p=p;self.y=y;self.signals=signals
 def __len__(self):return len(self.p)
 def __getitem__(self,key):
  if isinstance(key,str):return self.p if key=='p' else self.y if key=='y' else self.signals
  return Records(self.p[key],self.y[key],self.signals[key])
def columns(records,arm):
 p=records['p'].astype(np.float64);X=np.empty((len(records),2+len(arms[arm])),np.float64);X[:,0]=1;X[:,1]=np.log(p/(65536-p))
 for j,k in enumerate(arms[arm]):X[:,j+2]=records['signals'][:,k]
 return X
def inv(c):
 if 123<=c<127:c+=80-123
 elif 80<=c<84:c-=80-123
 elif 58<=c<=63 or 74<=c<=79:c^=0x70
 if c in (88,96):c^=88^96
 return c
def wordcode(j):
 if j<80:v=[128+j]
 elif j<3920:j-=80;v=[208+j//80,128+j%80]
 else:j-=3920;v=[240+(j//80)//32,208+(j//80)%32,128+j%80]
 return bytes(map(inv,v))
def dictionary_index(pending):
 first=pending[0]
 if first<208:return first-128
 if len(pending)<2:return None
 second=pending[1]
 if second<208:
  assert 128<=second<208
  return 80+(first-208)*80+second-128
 if len(pending)<3:return None
 assert first>=240 and 208<=second<240 and 128<=pending[2]<208
 return 3920+((first-240)*32+second-208)*80+pending[2]-128
constructors=set('the a an is are was were be been being and or but if then as at by for from in of on to with that which who whom whose this these those it its he she they we you i not no now there here when where how what why do does did have has had can could shall should will would may might must than so all any some such also into over under between through after before during'.split())
def roles(raw,words,stop=None):
 if stop is not None:raw=raw[:stop]
 marker=b''
 for piece in re.findall('[a-z]+|[^a-z]','  <page>\\n    <title>'):marker+=wordcode(words.index(piece)) if piece.isalpha() else bytes([inv(ord(piece))])
 start=raw.find(marker)+len(marker);assert start>=len(marker);role=np.zeros((len(raw),6),np.float32);prev=last=0;pending=[];escape=False
 for i,c in enumerate(raw):
  if prev:role[i,prev-1]=1
  if last:role[i,3+last]=1
  if i<start:continue
  if escape:escape=False;prev=4;continue
  pending.append(inv(c))
  if pending[0]<128:assert len(pending)==1;prev=3;escape=pending[0]==12;pending=[];continue
  j=dictionary_index(pending)
  if j is None:continue
  assert 0<=j<len(words);prev=last=1 if words[j] in constructors else 2;pending=[]
 return np.repeat(role,8,axis=0)
'''
body='''
try:
 save('waiting for exact stage-source identity/exports; no duplicate inference');deadline=time.monotonic()+7200
 while True:
  p=S/'manifest.json';sm=json.loads(p.read_text()) if p.exists() else {}
  if sm.get('status','').startswith('COMPLETE') or sm.get('status')=='FAIL':break
  if time.monotonic()>deadline:raise RuntimeError('parent still running; preserve dependent job, inspect before any relaunch')
  time.sleep(30)
 assert sm['status']=='COMPLETE_NATIVE_STAGE_IDENTITY_AND_AB_EXPORTS' and len(sm['controls'])==2 and len(sm['exports'])==2 and all(v['archive_identity'] and v['Q16_identity'] and v['independent_decode_exact'] for v in sm['controls'])
 nm=json.loads((N/'manifest.json').read_text());dictionary=R/'native_hidden_trace_v1/tree/dictionary/english.dic';words=re.findall('[a-z]+',dictionary.read_text());assert len(words)==44515 and sha(dictionary)==nm['dictionary_sha256'];m['production_stream']=nm['production_stream'];m['parent_stage_manifest_sha256']=sha(p);m['parent_observer_controls']=sm['controls'];m['source_hashes']=[{'file':n,'sha256':sha(R/n)} for n in ['research_round8_native_stage_fit_worker.py','research_round8_native_stage_fit_protocol.md']];m['feature_exports']=[];data={}
 # Independent code-index inverse across every dictionary entry, not a few examples.
 for j in range(44515):
  a=list(map(inv,wordcode(j)));k=a[0]-128 if len(a)==1 else 80+(a[0]-208)*80+a[1]-128 if len(a)==2 else 3920+((a[0]-240)*32+a[1]-208)*80+a[2]-128
  assert k==j and dictionary_index(a)==j
  for cut in range(1,len(a)):assert dictionary_index(a[:cut]) is None
 m['all_44515_wordcodes_inverse']='PASS'
 def export(s):
  n=next(v for v in nm['native_exports'] if v['slice']==s);v=next(v for v in sm['exports'] if v['slice']==s);root=S/(s+'512k');f=root/'stage.f32';assert sha(f)==v['stage_sha256'];pp=N/(s+'_native/final_p.u16');assert sha(pp)==n['final_p_sha256'];raw=(N/(s+'512k.bin')).read_bytes();assert hashlib.sha256(raw).hexdigest()==n['input_sha256'];p=np.fromfile(pp,dtype='<u2');ell=np.log(p.astype(np.float64)/(65536.-p));y=((np.frombuffer(raw,np.uint8)[:,None]>>(7-np.arange(8)))&1).astype(np.uint8).reshape(-1);frames=np.memmap(f,mode='r',dtype='<f4',offset=12,shape=(len(p),19));h=np.memmap(N/(s+'_native/hidden.q8'),dtype=np.uint8,mode='r',shape=(len(raw),193));valid=np.repeat(np.r_[np.uint8(0),h[:-1,0]],8).astype(np.float32);sig=np.empty((len(p),49),np.float32)
  sig[:,:14]=np.clip(frames[:,:14],-12,12)/12
  for j,k in enumerate([14,18,17]):
   prob=np.clip(frames[:,k].astype(np.float64),1/65536,65535/65536);sig[:,14+j]=np.clip(np.log(prob/(1-prob))-ell,-12,12)/12
  sig[:,17]=sig[:,16]*valid;sig[:,18]=sig[:,16]*((frames[:,17]>=.5)!=(frames[:,18]>=.5));sig[:,19]=np.clip(np.std(frames[:,:12].astype(np.float64),axis=1)/12,0,1);sig[:,20]=sig[:,16]*(4*(p.astype(np.float64)/65536)*(1-p.astype(np.float64)/65536));sig[:,21:23]=0
  sig[:128,23:37]=0;sig[128:,23:37]=sig[:-128,:14];sig[:,37:43]=roles(raw,words);sig[:128,43:49]=0;sig[128:,43:49]=sig[:-128,37:43];assert np.isfinite(sig).all();data[s]=Records(p,y,sig);row={'slice':s,'stage_sha256':v['stage_sha256'],'native_p_sha256':n['final_p_sha256'],'input_sha256':n['input_sha256'],'feature_sha256':hashlib.sha256(sig.tobytes()).hexdigest(),'feature_dimensions':49,'feature_bytes':sig.nbytes};m['feature_exports'].append(row);save('prefix-known source/role features '+s+' assembled')
 for s in 'ab':export(s)
 rng=np.random.default_rng(18218);X=rng.normal(size=(89,12));l=rng.normal(size=89);y=rng.integers(0,2,size=89);t=rng.uniform(-.3,.3,size=12);z=l+X@t;q=expit(z);g=X.T@(q-y);H=X.T@((q*(1-q))[:,None]*X);eps=1e-5
 def toy(t):z=l+X@t;return np.sum(np.logaddexp(0,z)-y*z)
 fd=np.array([(toy(t+np.eye(12)[j]*eps)-toy(t-np.eye(12)[j]*eps))/(2*eps) for j in range(12)]);err=float(np.max(np.abs(fd-g)));mineig=float(np.linalg.eigvalsh(H).min());assert err<1e-7 and mineig>=0;m['independent_math_test']={'gradient_error':err,'Hessian_min_eigenvalue':mineig}
 # Compare actual integer laws for every registered head, including nonzero coefficients.
 rec=data['a'];future=Records(rec.p[:8192].copy(),rec.y[:8192].copy(),rec.signals[:8192].copy());future.y[4096:]^=1;future.signals[4096:]=1;future.p[4096:]=65535-future.p[4096:]
 prefix_hash=hashlib.sha256()
 for arm in range(len(arms)):
  original=columns(rec[:4096],arm);changed=columns(future[:4096],arm);assert np.array_equal(original,changed)
  test_theta=np.linspace(-.2,.2,original.shape[1]);test_theta[1]=.03
  offset=np.log(rec.p[:4096].astype(np.float64)/(65536.-rec.p[:4096]));q0=np.clip(np.floor(65536*expit(offset+original@test_theta)+.5),1,65535).astype('<u2');q1=np.clip(np.floor(65536*expit(offset+changed@test_theta)+.5),1,65535).astype('<u2');assert np.array_equal(q0,q1);prefix_hash.update(q0.tobytes())
 raw=(N/'a512k.bin').read_bytes();altered=raw[:4096]+bytes([0])*(len(raw)-4096);assert np.array_equal(roles(raw,words)[:4096*8],roles(altered,words,stop=4096))
 m['future_target_source_role_noninterference']={'status':'PASS','heads':31,'earlier_integer_predictions_sha256':prefix_hash.hexdigest(),'prefix_bit_events':4096,'raw_role_prefix_bytes':4096};save('unweighted bounded fitting; no confirmation used')
 for arm,name in enumerate(names):
  start=time.monotonic();t,hist,solver=solve([data['a'],data['b']],arm);_,g,_=summation([data['a'],data['b']],arm,t);cert=gap(t,g);evals=[dict(slice=s,**evaluate(data[s],arm,t)) for s in 'ab'];gain=sum(v['q16_saving_bytes'] for v in evals);row={'name':name,'arm':arm,'coefficients':t.tolist(),'coefficient_bytes_per_copy':8*len(t),'supporting_plane_gap_bytes':cert,'ideal_box_optimum_certified':cert<=.05,'solver':solver,'iteration_history':hist,'fit_evaluate_wall_seconds':time.monotonic()-start,'evaluations':evals,'development_q16_saving_bytes':gain,'development_after_two_coefficient_copies_and_5bit_selector_bytes':gain-16*len(t)-.625};m['results'].append(row);save('fit '+name);assert cert<=.05
 best=max(m['results'],key=lambda v:v['development_after_two_coefficient_copies_and_5bit_selector_bytes']);m['selected_development_head']=best['name'];m['best_priced_AB_bytes']=best['development_after_two_coefficient_copies_and_5bit_selector_bytes'];m['advance_gate_pass']=m['best_priced_AB_bytes']>=64;m.update(status='COMPLETE_NATIVE_STAGE_FINITE_FIT',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('finite fit complete; if gate passes preserve then freeze conditional native C/D protocol')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved; do not duplicate');raise
'''
source=(prelude+helpers+body).replace('native_stage_fit_v1','native_stage_fit_v2').replace('research_round8_native_stage_fit_worker.py','research_round8_native_stage_fit_worker_v2.py').replace('research_round8_native_stage_fit_protocol.md','research_round8_native_stage_fit_protocol_v2.md')
project_path('research_round8_native_stage_fit_worker_v2.py').write_text(source)
project_path('research_round8_native_stage_fit_launch_v2.py').write_text('''import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'native_stage_fit_v1').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_native_stage_fit_worker.py')],stdout=(R/'native_stage_fit_v1_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'native_stage_fit_v1','depends_on':'native_stage_trace_v1','paid_spending_usd':0,'deletions':[]}))
'''.replace('native_stage_fit_v1','native_stage_fit_v2').replace('research_round8_native_stage_fit_worker.py','research_round8_native_stage_fit_worker_v2.py'))
