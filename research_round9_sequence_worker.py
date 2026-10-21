"""Causal learned sequence descendants over exact native before-target sources.

This is a new residual architecture experiment, not original-core finetuning.
Every target, including literals and OOVs, is scored without loss masking.
"""
import os,sys
os.environ['CUDA_VISIBLE_DEVICES']='1';os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import pathlib,json,time,hashlib,traceback,math
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
R=pathlib.Path('/kaggle/working/hp_round8');OUT=pathlib.Path('/kaggle/working/hp_round9');D=OUT/'causal_sequence_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scope':'learned causal source-sequence residuals, full bit loss; original core frozen','deletions':[],'spending_usd':0,'rungs':[],'confirmation':[]}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Head(nn.Module):
 def __init__(self,kind,width):
  super().__init__();self.kind=kind;self.proj=nn.Linear(10,width)
  if kind=='gru':self.body=nn.GRU(width,width,2,batch_first=True)
  elif kind=='attention':self.body=nn.TransformerEncoder(nn.TransformerEncoderLayer(width,4,4*width,dropout=0,batch_first=True,activation='gelu',norm_first=True),2,enable_nested_tensor=False)
  elif kind=='tcn':self.body=nn.ModuleList([nn.Conv1d(width,width,3,dilation=d) for d in [1,4,16,64]])
  else:self.body=nn.Sequential(nn.Linear(width,width),nn.GELU(),nn.Linear(width,width),nn.GELU())
  self.out=nn.Linear(width,1);nn.init.zeros_(self.out.weight);nn.init.zeros_(self.out.bias)
 def forward(self,x):
  h=F.gelu(self.proj(x))
  if self.kind=='gru':h,_=self.body(h)
  elif self.kind=='attention':
   pos=torch.arange(h.shape[1],device=h.device,dtype=h.dtype);dims=torch.arange(h.shape[2],device=h.device,dtype=h.dtype)
   angle=pos[:,None]/10000**(2*torch.floor(dims/2)/h.shape[2]);h=h+torch.where((dims.to(torch.long)%2)==0,torch.sin(angle),torch.cos(angle))[None]*.1
   mask=torch.triu(torch.ones(h.shape[1],h.shape[1],device=h.device,dtype=torch.bool),1);h=self.body(h,mask=mask,is_causal=True)
  elif self.kind=='tcn':
   h=h.transpose(1,2)
   for conv in self.body:h=h+F.gelu(conv(F.pad(h,(2*conv.dilation[0],0))))
   h=h.transpose(1,2)
  else:h=self.body(h)
  return .5*torch.tanh(self.out(h).squeeze(-1))
def load_slice(s):
 N=R/'atom_cache_v1';stage=R/'native_stage_trace_v1' if s in 'ab' else R/'native_stage_weak_confirmation_v1' if s in 'cd' else R/'source_wide_confirmation_v1'
 root=stage/(s+'512k');rawpath=N/(s+'512k.bin') if s in 'abcd' else root/'input.bin';raw=rawpath.read_bytes()
 pp=N/(s+'_native/final_p.u16') if s in 'abcd' else root/'final_p.u16';p=np.fromfile(pp,'<u2').astype(np.float64);assert len(p)==8*len(raw)
 st=np.memmap(root/'stage.f32','<f4','r',offset=12,shape=(len(p),19));hp=N/(s+'_native/hidden.q8') if s in 'abcd' else root/'hidden.q8';h=np.memmap(hp,'u1','r',shape=(len(raw),193));valid=np.repeat(np.r_[0,h[:-1,0]],8)
 ell=np.log(p/(65536-p));x=np.empty((len(p),10),np.float32);x[:,0]=ell/12
 for j,k in enumerate([17,18,14]):
  q=np.clip(st[:,k].astype(np.float64),1/65536,65535/65536);x[:,j+1]=np.clip(np.log(q/(1-q))-ell,-12,12)/12
 x[:,1]*=valid;x[:,4]=4*p/65536*(1-p/65536);x[:,5]=(np.arange(len(p))%8)/7;x[:,6]=valid;x[:,7]=1
 y=((np.frombuffer(raw,'u1')[:,None]>>(7-np.arange(8)))&1).astype(np.float32).reshape(-1)
 x[:,8]=np.r_[0,y[:-1]];x[:,9]=np.repeat(np.r_[0,np.frombuffer(raw,'u1')[:-1]],8)/255
 theta=np.array(json.loads((R/'source_wide_box_v1/manifest.json').read_text())['coefficients']);offset=(ell+theta[0]+theta[1]*ell+theta[2]*x[:,1]).astype(np.float32)
 m.setdefault('inputs',[]).append({'slice':s,'raw_path':str(rawpath),'raw_sha256':sha(rawpath),'probability_sha256':sha(pp),'stage_sha256':sha(root/'stage.f32')})
 return {'x':x,'offset':offset,'y':y,'p':p}
def blocks(rec):return {k:torch.as_tensor(v.reshape(-1,512,10) if k=='x' else v.reshape(-1,512),device='cuda') for k,v in rec.items() if k in ['x','offset','y']}
def score(model,rec):
 model.eval();gain=wide=0.;hashq=hashlib.sha256();t=time.monotonic();block=512;count=0
 with torch.no_grad():
  for start in range(0,len(rec['y']),block*64):
   end=min(start+block*64,len(rec['y']));x=torch.as_tensor(rec['x'][start:end].reshape(-1,block,10),device='cuda');d=model(x).reshape(-1).cpu().numpy().astype(np.float64);z=rec['offset'][start:end].astype(np.float64)+d
   q=np.clip(np.floor(65536/(1+np.exp(-z))+.5),1,65535).astype('<u2');base=np.clip(np.floor(65536/(1+np.exp(-rec['offset'][start:end].astype(np.float64)))+.5),1,65535)
   y=rec['y'][start:end].astype(bool);sel=np.where(y,q.astype(np.float64),65536-q.astype(np.float64));p=rec['p'][start:end];gain+=float(np.log2(sel/np.where(y,p,65536-p)).sum()/8);wide+=float(np.log2(sel/np.where(y,base,65536-base)).sum()/8);hashq.update(q.tobytes());count+=len(q)
 return {'gain_vs_native_bytes':gain,'gain_vs_wide_bytes':wide,'Q16_sha256':hashq.hexdigest(),'targets':count,'inference_seconds':time.monotonic()-t}
try:
 torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.manual_seed(6206);m['gpu']=torch.cuda.get_device_name(0);m['worker_sha256']=sha(OUT/'research_round9_sequence_worker.py');save('loading actual native sources; no masking or sparse-prior replacement')
 data={s:load_slice(s) for s in 'abcd'};train={k:np.concatenate([data[s][k] for s in 'ab']) for k in data['a']};dev={k:np.concatenate([data[s][k] for s in 'cd']) for k in data['c']};del data
 tb=blocks(train);m['contract']={'block_bits':512,'state_reset':'fixed absolute bit-block boundaries, every512bits','targets':'all8bits of every original WRT byte','train_slices':'A/B','development_slices':'C/D already observed in other experiment families','confirmation_slices':'E/F fit-held-out, not globally untouched','batch_blocks':16,'nonzero_targets_per_step':8192,'learning_rate':.0003,'residual_limit_logodds':.5,'model_cost':'FP32 parameter bytes and zlib9 weight bytes; native executable and CPU qualification pending'}
 arms=[(kind,w) for kind in ['mlp','gru','tcn','attention'] for w in [32,64]];models={};opts={};steps={};survivors=arms[:]
 for kind,w in arms:
  key=f'{kind}{w}';torch.manual_seed(6206);model=Head(kind,w).cuda();models[key]=model;opts[key]=torch.optim.AdamW(model.parameters(),lr=.0003,weight_decay=.01);steps[key]=0
  # Nonzero-output causal challenge tests the architecture, not only the zero head.
  with torch.no_grad():model.out.weight.fill_(.001);model.out.bias.fill_(.01);probe=tb['x'][:1].clone();a=model(probe);probe[:,256:]=torch.randn_like(probe[:,256:]);b=model(probe);assert torch.equal(a[:,:256],b[:,:256]),key+'future-dependent prefix';model.out.weight.zero_();model.out.bias.zero_()
  assert score(model,{k:v[:512] for k,v in dev.items()})['gain_vs_wide_bytes']==0
 m['nonzero_future_prefix_and_zero_residual_identity']='PASS';save('causal identity gates passed; beginning8architecture arms')
 import zlib
 for rung in [128,384,1152]:
  for kind,w in survivors:
   key=f'{kind}{w}';model=models[key];opt=opts[key];model.train();t=time.monotonic();generator=torch.Generator(device='cuda').manual_seed(6206+steps[key]*101)
   while steps[key]<rung:
    ix=torch.randint(tb['y'].shape[0],(16,),device='cuda',generator=generator);opt.zero_grad(set_to_none=True);loss=F.binary_cross_entropy_with_logits(tb['offset'][ix]+model(tb['x'][ix]),tb['y'][ix]);loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();steps[key]+=1
    if steps[key]%64==0:save(key+' step'+str(steps[key]))
   torch.cuda.synchronize();train_s=time.monotonic()-t;result=score(model,dev);param=np.concatenate([v.detach().cpu().numpy().reshape(-1) for v in model.parameters()]).astype('<f4');path=D/f'{key}_step{rung}.pt';torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'steps':rung,'arm':[kind,w],'seed':6206},path);m['rungs'].append({'arm':key,'step':rung,'parameter_count':len(param),'FP32_parameter_bytes':param.nbytes,'zlib9_weight_bytes':len(zlib.compress(param.tobytes(),9)),'training_seconds_this_rung':train_s,'checkpoint_sha256':sha(path),'development':result});save(key+' rung'+str(rung)+' scored')
  ranking=sorted(survivors,key=lambda a:next(r['development']['gain_vs_wide_bytes'] for r in reversed(m['rungs']) if r['arm']==f'{a[0]}{a[1]}' and r['step']==rung),reverse=True)
  if rung<1152:survivors=ranking[:4 if rung==128 else 2];m.setdefault('locked_selections',[]).append({'rung':rung,'survivors':[f'{a[0]}{a[1]}' for a in survivors]});save('development-only successive halving locked')
 m['frozen_finalists']=[f'{a[0]}{a[1]}' for a in survivors];save('finalists frozen before E/F; loading confirmation')
 for s in 'ef':
  rec=load_slice(s)
  for kind,w in survivors:m['confirmation'].append({'slice':s,'arm':f'{kind}{w}','result':score(models[f'{kind}{w}'],rec)});save('confirmed '+s)
 m.update(status='COMPLETE_CAUSAL_SEQUENCE_RESIDUAL_ARCHITECTURE_SCREEN',finished=time.time(),peak_gpu_bytes=torch.cuda.max_memory_allocated(),native_integration=False,all96_exhausted=False);save('screen complete; native and full package gates still required')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
