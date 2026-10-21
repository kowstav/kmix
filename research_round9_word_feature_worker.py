"""Controlled completed-word spelling, glyph and constructor-state descendants.

Training begins once A/B event extraction is provably complete, while full
prefix verification continues. C/D selection and E/F confirmation wait for its
PASS manifest. No rare-frequency, next-word or right-context labels are inputs.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='0';os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import pathlib,json,time,hashlib,traceback,math,ast,zlib
import numpy as np,torch
from torch import nn
from torch.nn import functional as F
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'word_features_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/word_features_v1');S.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scope':'causal completed-word letter/shape/placement combinations with matched controls; core frozen','spending_usd':0,'deletions':[],'rungs':[],'confirmation':[],'scratch':str(S)}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ctor=set('the a an and or but if then than that this these those it its is are was were be been being as at by for from in into of on onto to with without not no now there here i you he she we they which who when where why how all any each some such more most less very can could will would may might must do does did have has had'.split())
glyph_groups=['bcdgopq','aeo','bdhklt','gpqy','ij','mntuvw','sz','aceios']
def spelling(w):
 bag=np.bincount([ord(c)-97 for c in w if 'a'<=c<='z'],minlength=26).astype(np.float32);bag/=max(1,float(bag.sum()));pos=np.zeros(8,np.int64)
 for i,c in enumerate(w[:4]):pos[i]=ord(c)-96 if 'a'<=c<='z' else 0
 for i,c in enumerate(w[-4:]):pos[4+i]=ord(c)-96 if 'a'<=c<='z' else 0
 geo=np.array([sum(c in g for c in w)/max(1,len(w)) for g in glyph_groups],np.float32)
 return bag,pos,geo
def features(events,start,n,randomize=False):
 form=np.zeros((n,60),np.float32);pos=np.zeros((n,8),np.int64);role=np.zeros((n,12),np.float32);ident=np.zeros((n,2),np.int64);last='';noun='';flags=[0.,0.,0.,0.];run=0;lastend=0;prevbag=np.zeros(26,np.float32);cursor=0
 def state(word):
  bag,po,geo=spelling(word);seed=int(hashlib.sha256(word.encode()).hexdigest()[:16],16)
  if randomize:
   gen=np.random.default_rng(seed);b=gen.standard_normal(26).astype(np.float32);b/=max(1.,float(np.linalg.norm(b)));bag=b;geo=gen.standard_normal(8).astype(np.float32)/3;po=gen.integers(0,27,8)
  return bag,po,geo
 for lo,hi,complete,word in events:
  at=complete-start;assert 16<=lo-start and lo<=hi<=complete and 0<=at<=n
  if at>cursor:
   form[cursor:at]=np.r_[state(last)[0],prevbag,state(last)[2]];pos[cursor:at]=state(last)[1];ident[cursor:at,0]=int(hashlib.sha256(last.encode()).hexdigest()[:8],16)%512;ident[cursor:at,1]=int(hashlib.sha256(noun.encode()).hexdigest()[:8],16)%512
   role[cursor:at,:4]=flags;role[cursor:at,4]=min(run,16)/16;role[cursor:at,5]=min(len(last),32)/32;role[cursor:at,6]=min(len(noun),32)/32;role[cursor:at,7]=np.minimum(np.arange(cursor,at)-lastend,256)/256;role[cursor:at,8]=float(last in ctor);role[cursor:at,9]=float(noun==last);role[cursor:at,10]=float(bool(last));role[cursor:at,11]=1.
  prevbag=state(last)[0];last=word;isc=word in ctor;flags=[float(isc),*flags[:3]];run=run+1 if isc else 0
  if not isc:noun=word
  lastend=at;cursor=at
 if cursor<n:
  form[cursor:]=np.r_[state(last)[0],prevbag,state(last)[2]];pos[cursor:]=state(last)[1];ident[cursor:,0]=int(hashlib.sha256(last.encode()).hexdigest()[:8],16)%512;ident[cursor:,1]=int(hashlib.sha256(noun.encode()).hexdigest()[:8],16)%512;role[cursor:,:4]=flags;role[cursor:,4]=min(run,16)/16;role[cursor:,5]=min(len(last),32)/32;role[cursor:,6]=min(len(noun),32)/32;role[cursor:,7]=np.minimum(np.arange(cursor,n)-lastend,256)/256;role[cursor:,8]=float(last in ctor);role[cursor:,9]=float(noun==last);role[cursor:,10]=float(bool(last));role[cursor:,11]=1.
 return {'form':form,'position':pos,'role':role,'identity':ident}
class Model(nn.Module):
 def __init__(self,arm):
  super().__init__();self.arm=arm;self.letter=nn.Embedding(27,3);self.word=nn.Embedding(512,4);self.proj=nn.Linear(60+24+12+8,32);self.head=nn.Sequential(nn.Linear(32+8+32,32),nn.GELU(),nn.Linear(32,1));nn.init.zeros_(self.head[-1].weight);nn.init.zeros_(self.head[-1].bias)
 def forward(self,x,form,position,role,identity):
  ff=form.clone();pp=self.letter(position).flatten(-2);rr=role;ii=self.word(identity).flatten(-2)
  if self.arm=='native_control':ff=ff*0;pp=pp*0;rr=rr*0;ii=ii*0
  if self.arm=='identity':ff=ff*0;pp=pp*0;rr=rr*0
  if self.arm=='bag_positions':ff[...,52:]=0;rr=rr*0;ii=ii*0
  if self.arm=='glyph':ff[...,:52]=0;pp=pp*0;rr=rr*0;ii=ii*0
  if self.arm=='grammar':ff=ff*0;pp=pp*0;ii=ii*0
  if self.arm in ['spelling_grammar','spelling_cross']:ff[...,52:]=0;ii=ii*0
  h=F.gelu(self.proj(torch.cat([ff,pp,rr,ii],-1)));h=h[:,:,None].expand(-1,-1,8,-1);cross=h*x[...,1,None] if self.arm in ['spelling_cross','all','random_word_vectors'] else h*0
  z=self.head(torch.cat([h,x,cross],-1)).squeeze(-1);return .5*torch.tanh(z)
def load_events():
 rows=[[] for _ in range(6)];manifest=json.loads((R/'word_events_v1/manifest.json').read_text())
 for line in pathlib.Path(manifest['scratch'],'events.tsv').open():
  fields=line.rstrip().split('\t')
  if len(fields)!=6:continue
  idx,lo,hi,complete,body,word=fields;rows[int(idx)].append((int(lo),int(hi),int(complete),word))
 return rows,manifest
def load_data(s,rows,manifest,randomize=False):
 rec=load_native(s);window=next(v for v in manifest['windows'] if v['slice']==s);e=rows[list('abcdef').index(s)];f=features(e,window['start'],len(rec['y']),randomize);rec.update(f)
 # Recover the original FP64 frozen law for scoring (training tensor may be FP32).
 ell=np.log(rec['p']/(65536-rec['p']));theta=np.array(json.loads((pathlib.Path('/kaggle/working/hp_round8/source_wide_box_v1/manifest.json')).read_text())['coefficients']);rec['offset']=ell+theta[0]+theta[1]*ell+theta[2]*rec['x'][:,:,1].astype(np.float64);return rec
def blocks(rec,L):return {k:torch.as_tensor(v[:len(v)//L*L].reshape((-1,L)+v.shape[1:]),device='cuda') for k,v in rec.items() if k in ['x','form','position','role','identity','offset','y']}
def score(model,rec,L):
 model.eval();gain=extra=0.;qh=hashlib.sha256()
 with torch.no_grad():
  for start in range(0,len(rec['y']),L*16):
   n=min(L*16,len(rec['y'])-start)//L*L
   if not n:continue
   bb={k:torch.as_tensor(rec[k][start:start+n].reshape((-1,L)+rec[k].shape[1:]),device='cuda') for k in ['x','form','position','role','identity']};d=model(**bb).cpu().numpy().reshape(n,8).astype(np.float64);off=rec['offset'][start:start+n];q=np.clip(np.floor(65536/(1+np.exp(-(off+d)))+.5),1,65535).astype('<u2');base=np.clip(np.floor(65536/(1+np.exp(-off))+.5),1,65535);y=rec['y'][start:start+n].astype(bool);p=rec['p'][start:start+n];sel=np.where(y,q.astype(np.float64),65536-q.astype(np.float64));gain+=float(np.log2(sel/np.where(y,p,65536-p)).sum()/8);extra+=float(np.log2(sel/np.where(y,base,65536-base)).sum()/8);qh.update(q.tobytes())
 return {'gain_vs_native_bytes':gain,'gain_vs_wide_bytes':extra,'Q16_sha256':qh.hexdigest()}
try:
 torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;m['gpu']=torch.cuda.get_device_name(0);m['worker_sha256']=sha(R/'research_round9_word_feature_worker.py')
 # Import only the frozen native-source loader, not its previous training loop.
 tree=ast.parse((R/'research_round9_hidden_sequence_worker_v2.py').read_text());fs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load'];ns={'np':np,'torch':torch,'R':pathlib.Path('/kaggle/working/hp_round8'),'m':m,'json':json,'sha':sha};exec(compile(ast.Module(body=fs,type_ignores=[]),'<native-feature-loader>','exec'),ns);load_native=ns['load']
 save('waiting for immutable A/B complete-word extraction prefix')
 while True:
  rows,manifest=load_events()
  if manifest['status']=='FAIL':raise RuntimeError(manifest.get('error'))
  if rows[4] or manifest['status']=='COMPLETE_CAUSAL_WHOLE_WORD_EVENTS':break
  time.sleep(15)
 m['AB_prefix_complete_proof']='E at190M emitted; all A/B windows end before103.16M';events=rows;arm_names=['native_control','identity','bag_positions','glyph','grammar','spelling_grammar','spelling_cross','all','random_word_vectors'];seeds=[6706,6707];models={};opts={};steps={};L=128;data={s:load_data(s,rows,manifest) for s in 'ab'};train={k:np.concatenate([data[s][k] for s in 'ab']) for k in data['a'] if k in ['x','form','position','role','identity','offset','y']};tb=blocks(train,L);random_data={s:load_data(s,rows,manifest,True) for s in 'ab'};random_train={k:np.concatenate([random_data[s][k] for s in 'ab']) for k in train};rtb=blocks(random_train,L)
 m['contract']={'arms':arm_names,'seeds':seeds,'rungs':[128,384,1152],'history':'completed words only; injected after delimiter completion; no frequency/target/intext labels','lexical_body_mode':'known canonical WRT semantic body, first16bytes/cross-boundary words excluded; future native integration must reproduce parser state','grammar':'fixed constructor lexicon is a heuristic class, not POS truth; other words are content-like, not nouns proven by syntax','glyph':'hand-coded symbolic groups, not raster CNN or OCR codec','random_control':'deterministic word-hash vectors replacing spelling sharing with matched architecture; not an information-theoretic null','combination':'word state plus current native-source disagreement, including a learned bilinear interaction','core':'unchanged','all96_exhausted':False,'native_integration':'pending'}
 for seed in seeds:
  for arm in arm_names:
   key=f'{arm}_seed{seed}';torch.manual_seed(seed);model=Model(arm).cuda();models[key]=model;opts[key]=torch.optim.AdamW(model.parameters(),lr=.0003,weight_decay=.01);steps[key]=0
   probe={k:tb[k][:1].clone() for k in ['x','form','position','role','identity']}
   with torch.no_grad():
    model.head[-1].weight.fill_(.001);a=model(**probe);probe['form'][:,64:]=1;probe['position'][:,64:]=1;probe['role'][:,64:]=1;probe['identity'][:,64:]=1;probe['x'][:,64:]=1;assert torch.equal(a[:,:64],model(**probe)[:,:64]);model.head[-1].weight.zero_()
   assert score(model,{k:v[:L] for k,v in data['a'].items()},L)['gain_vs_wide_bytes']==0
 m['nonzero_future_prefix_and_zero_identity']='PASS'
 def train_to(key,rung):
  model=models[key];model.train();opt=opts[key];batch=rtb if model.arm=='random_word_vectors' else tb;gen=torch.Generator(device='cuda').manual_seed(int(key.split('seed')[-1])+steps[key]*101);start=time.monotonic()
  while steps[key]<rung:
   ix=torch.randint(batch['y'].shape[0],(16,),device='cuda',generator=gen);bb={k:batch[k][ix] for k in ['x','form','position','role','identity']};opt.zero_grad(set_to_none=True);z=batch['offset'][ix].float()+model(**bb);F.binary_cross_entropy_with_logits(z,batch['y'][ix]).backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();steps[key]+=1
  path=S/(key+'_step'+str(rung)+'.pt');torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'step':rung,'key':key},path);buf=b''.join(v.detach().cpu().numpy().tobytes() for v in model.state_dict().values());row={'key':key,'step':rung,'training_seconds':time.monotonic()-start,'checkpoint_sha256':sha(path),'checkpoint_path':str(path),'parameters':sum(p.numel() for p in model.parameters()),'zlib9_model_bytes':len(zlib.compress(buf,9))};m['rungs'].append(row);save(key+' rung'+str(rung)+' trained');return row
 for rung in [128,384]:
  for key in models:train_to(key,rung)
 save('A/B architecture fits complete; awaiting full event extraction PASS before C/D')
 while True:
  rows,manifest=load_events()
  if manifest['status']=='FAIL':raise RuntimeError(manifest.get('error'))
  if manifest['status']=='COMPLETE_CAUSAL_WHOLE_WORD_EVENTS':break
  time.sleep(15)
 m['whole_native_word_decoder_verified']=True;m['event_manifest_sha256']=sha(R/'word_events_v1/manifest.json')
 development={s:load_data(s,rows,manifest) for s in 'cd'};random_dev={s:load_data(s,rows,manifest,True) for s in 'cd'}
 for key,model in models.items():
  results=[score(model,(random_dev if model.arm=='random_word_vectors' else development)[s],L) for s in 'cd'];row=next(v for v in reversed(m['rungs']) if v['key']==key and v['step']==384);row['development']=results;save(key+' C/D scored')
 survivors=[]
 for seed in seeds:
  ranked=sorted([v for v in m['rungs'] if v['step']==384 and v['key'].endswith('seed'+str(seed))],key=lambda v:sum(r['gain_vs_wide_bytes'] for r in v['development']),reverse=True);survivors.extend(v['key'] for v in ranked[:2])
 m['frozen_finalists']=survivors;save('C/D finalists frozen before longer training and E/F')
 for key in survivors:
  row=train_to(key,1152);model=models[key];row['development']=[score(model,(random_dev if model.arm=='random_word_vectors' else development)[s],L) for s in 'cd']
 for s in 'ef':
  normal=load_data(s,rows,manifest);random=load_data(s,rows,manifest,True)
  for key in survivors:model=models[key];m['confirmation'].append({'slice':s,'key':key,'result':score(model,random if model.arm=='random_word_vectors' else normal,L)});save(key+' '+s+' confirmation')
 m.update(status='COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN',finished=time.time(),native_or_full_package_qualified=False,all96_exhausted=False);save('controlled word descendants complete; native integration and broader coverage remain open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
