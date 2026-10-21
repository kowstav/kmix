"""Byte-rate recurrent/TTL memory with full192-dimensional native state.

All model inputs derive from completed bytes or current before-target native
probabilities. Frequency labels and targets never enter the predictor inputs.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='1';os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import pathlib,json,time,traceback,hashlib,math
import torch,numpy as np
from torch import nn
from torch.nn import functional as F
R=pathlib.Path('/kaggle/working/hp_round8');OUT=pathlib.Path('/kaggle/working/hp_round9');D=OUT/'hidden_sequence_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[],'scope':'learned native-hidden-state, outcome memory and TTL descendants; original core frozen','rungs':[],'confirmation':[]}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Model(nn.Module):
 def __init__(self,kind,width):
  super().__init__();self.kind=kind;self.embed=nn.Embedding(257,16);self.proj=nn.Linear(192+16+3,width)
  if kind in ['gru','permuted_gru']:self.memory=nn.GRU(width,width,2,batch_first=True)
  elif kind in ['ttl','fixed_ttl']:self.logit_decay=nn.Parameter(torch.tensor([math.log(math.exp(-1/h)/(1-math.exp(-1/h))) for h in [1,8,64,512]]),requires_grad=kind=='ttl');self.combine=nn.Linear(4*width,width)
  else:self.memory=nn.Sequential(nn.Linear(width,width),nn.GELU(),nn.Linear(width,width))
  self.head=nn.Sequential(nn.Linear(width+8,32),nn.GELU(),nn.Linear(32,1));nn.init.zeros_(self.head[-1].weight);nn.init.zeros_(self.head[-1].bias)
 def forward(self,bit_features,history,byte):
  if self.kind=='permuted_gru':history=history[...,torch.arange(195,device=history.device).roll(17)] # fixed channel control, causal
  x=F.gelu(self.proj(torch.cat([history[...,:192],self.embed(byte),history[...,192:]],-1)))
  if self.kind in ['gru','permuted_gru']:h,_=self.memory(x)
  elif self.kind in ['ttl','fixed_ttl']:
   # Causal EWMA via a recurrence; no reverse pass or future token summation.
   state=torch.zeros(x.shape[0],4,x.shape[-1],device=x.device);rows=[];a=torch.sigmoid(self.logit_decay)[None,:,None]
   for t in range(x.shape[1]):state=a*state+(1-a)*x[:,t,None];rows.append(self.combine(state.flatten(1)))
   h=torch.stack(rows,1)
  else:h=self.memory(x)
  z=self.head(torch.cat([h[:,:,None,:].expand(-1,-1,8,-1),bit_features],-1)).squeeze(-1);return .5*torch.tanh(z)
def load(s):
 N=R/'atom_cache_v1';sr=R/'native_stage_trace_v1' if s in 'ab' else R/'native_stage_weak_confirmation_v1' if s in 'cd' else R/'source_wide_confirmation_v1';root=sr/(s+'512k');rawpath=N/(s+'512k.bin') if s in 'abcd' else root/'input.bin';raw=np.frombuffer(rawpath.read_bytes(),'u1').copy();pp=N/(s+'_native/final_p.u16') if s in 'abcd' else root/'final_p.u16';p=np.fromfile(pp,'<u2').reshape(-1,8).astype(np.float64);ell=np.log(p/(65536-p));hp=N/(s+'_native/hidden.q8') if s in 'abcd' else root/'hidden.q8';hidden=np.memmap(hp,'u1','r',shape=(len(raw),193));valid=np.r_[0,hidden[:-1,0]].astype(np.float32);before=np.vstack([np.zeros((1,192)),np.asarray(hidden[:-1,1:],np.float32)/127.5-1]);before*=valid[:,None];st=np.memmap(root/'stage.f32','<f4','r',offset=12,shape=(len(raw),8,19));x=np.zeros((len(raw),8,8),np.float32);x[:,:,0]=ell/12
 for j,k in enumerate([17,18,14]):q=np.clip(st[:,:,k].astype(np.float64),1/65536,65535/65536);x[:,:,j+1]=np.clip(np.log(q/(1-q))-ell,-12,12)/12
 x[:,:,1]*=valid[:,None];x[:,:,4]=4*p/65536*(1-p/65536);x[:,:,5]=np.arange(8)[None]/7;x[:,:,6]=valid[:,None];x[:,:,7]=1
 y=((raw[:,None]>>(7-np.arange(8)))&1).astype(np.float32);true=np.where(y,p,65536-p)/65536;surprise=np.r_[0,-np.log2(true[:-1]).sum(-1)/64].astype(np.float32);prev=np.r_[256,raw[:-1]].astype(np.int64);hist=np.column_stack([before,valid,surprise,np.r_[0,np.mean(y[:-1],-1)]]).astype(np.float32);theta=np.array(json.loads((R/'source_wide_box_v1/manifest.json').read_text())['coefficients']);offset=(ell+theta[0]+theta[1]*ell+theta[2]*x[:,:,1]).astype(np.float32);m.setdefault('inputs',[]).append({'slice':s,'raw_sha256':sha(rawpath),'native_p_sha256':sha(pp),'hidden_sha256':sha(hp),'stage_sha256':sha(root/'stage.f32')});return {'x':x,'history':hist,'byte':prev,'offset':offset,'y':y,'p':p}
def toblocks(rec,length):
 out={}
 for k,v in rec.items():out[k]=torch.as_tensor(v[:len(v)//length*length].reshape((-1,length)+v.shape[1:]),device='cuda')
 return out
def score(model,rec,length):
 model.eval();g=e=0.;qh=hashlib.sha256();t=time.monotonic()
 with torch.no_grad():
  for start in range(0,len(rec['y']),length*16):
   end=min(start+length*16,len(rec['y']));n=(end-start)//length*length;end=start+n
   if not n:continue
   b={k:torch.as_tensor(v[start:end].reshape((-1,length)+v.shape[1:]),device='cuda') for k,v in rec.items() if k in ['x','history','byte']};d=model(b['x'],b['history'],b['byte']).cpu().numpy().reshape(n,8).astype(np.float64);z=rec['offset'][start:end].astype(np.float64)+d;q=np.clip(np.floor(65536/(1+np.exp(-z))+.5),1,65535).astype('<u2');base=np.clip(np.floor(65536/(1+np.exp(-rec['offset'][start:end].astype(np.float64)))+.5),1,65535);y=rec['y'][start:end].astype(bool);p=rec['p'][start:end];sel=np.where(y,q.astype(np.float64),65536-q.astype(np.float64));g+=float(np.log2(sel/np.where(y,p,65536-p)).sum()/8);e+=float(np.log2(sel/np.where(y,base,65536-base)).sum()/8);qh.update(q.tobytes())
 return {'gain_vs_native_bytes':g,'gain_vs_wide_bytes':e,'Q16_sha256':qh.hexdigest(),'inference_seconds':time.monotonic()-t}
try:
 torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;m['gpu']=torch.cuda.get_device_name(0);m['worker_sha256']=sha(OUT/'research_round9_hidden_sequence_worker.py');save('assembling all192 causal native-state features and delayed outcome memory')
 data={s:load(s) for s in 'abcd'};train={k:np.concatenate([data[s][k] for s in 'ab']) for k in data['a']};dev={k:np.concatenate([data[s][k] for s in 'cd']) for k in data['c']};del data;L=128;tb=toblocks(train,L)
 arms=[(kind,w) for kind in ['mlp','gru','ttl','fixed_ttl','permuted_gru'] for w in [32,64]];m['contract']={'training_block_bytes':L,'reset':'fixed absolute128byte blocks; not unlimited retention','batch_blocks':16,'target_bits_per_step':L*16*8,'train':'A/B','development':'C/D','confirmation':'E/F not previously used for this fit; previously used by other fits','TTL_timescale_units':'completed bytes','fixed_vs_learned_decay_control':True,'permuted_control':'fixed rotation of native-state channels; channel relabeling does not destroy information and is not a semantic null','core_updates':'unchanged','native_production_status':'unintegrated'};models={};opts={};steps={}
 for kind,w in arms:
  key=f'{kind}{w}';torch.manual_seed(6406);model=Model(kind,w).cuda();models[key]=model;opts[key]=torch.optim.AdamW(model.parameters(),lr=.0003,weight_decay=.01);steps[key]=0
  with torch.no_grad():
   model.head[-1].weight.fill_(.001);model.head[-1].bias.fill_(.01);probe={k:v[:1].clone() for k,v in tb.items()};a=model(probe['x'],probe['history'],probe['byte']);probe['x'][:,64:]=1;probe['history'][:,64:]=7;probe['byte'][:,64:]=1;b=model(probe['x'],probe['history'],probe['byte']);assert torch.equal(a[:,:64],b[:,:64]),key+'causal prefix failed';model.head[-1].weight.zero_();model.head[-1].bias.zero_()
  assert score(model,{k:v[:L] for k,v in dev.items()},L)['gain_vs_wide_bytes']==0
 m['nonzero_future_prefix_and_zero_residual_identity']='PASS';survivors=arms[:];save('ten hidden-state and learned-TTL arms starting')
 for rung in [128,384,1152]:
  for kind,w in survivors:
   key=f'{kind}{w}';model=models[key];opt=opts[key];model.train();t=time.monotonic();gen=torch.Generator(device='cuda').manual_seed(6406+steps[key]*101)
   while steps[key]<rung:
    ix=torch.randint(tb['y'].shape[0],(16,),device='cuda',generator=gen);opt.zero_grad(set_to_none=True);z=tb['offset'][ix]+model(tb['x'][ix],tb['history'][ix],tb['byte'][ix]);loss=F.binary_cross_entropy_with_logits(z,tb['y'][ix]);loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();steps[key]+=1
    if steps[key]%64==0:save(key+' step'+str(steps[key]))
   torch.cuda.synchronize();secs=time.monotonic()-t;result=score(model,dev,L);path=D/f'{key}_step{rung}.pt';torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'steps':rung,'arm':[kind,w],'seed':6406},path);m['rungs'].append({'arm':key,'step':rung,'parameters':sum(v.numel() for v in model.parameters()),'training_seconds_this_rung':secs,'development':result,'checkpoint_sha256':sha(path)});save(key+' rung'+str(rung)+' scored')
  ranking=sorted(survivors,key=lambda a:next(v['development']['gain_vs_wide_bytes'] for v in reversed(m['rungs']) if v['arm']==f'{a[0]}{a[1]}' and v['step']==rung),reverse=True)
  if rung<1152:survivors=ranking[:4 if rung==128 else 2];m.setdefault('locked_selections',[]).append({'rung':rung,'survivors':[f'{a[0]}{a[1]}' for a in survivors]});save('development-only selection locked')
 m['frozen_finalists']=[f'{a[0]}{a[1]}' for a in survivors];save('finalists frozen before E/F')
 for s in 'ef':
  rec=load(s)
  for kind,w in survivors:m['confirmation'].append({'slice':s,'arm':f'{kind}{w}','result':score(models[f'{kind}{w}'],rec,L)});save('confirmation '+s)
 m.update(status='COMPLETE_NATIVE_HIDDEN_SEQUENCE_TTL_SCREEN',finished=time.time(),peak_gpu_bytes=torch.cuda.max_memory_allocated(),all96_exhausted=False);save('hidden-state and TTL screen complete; native/package gate open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
