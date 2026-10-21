import datetime,hashlib,json,os,pathlib,time,traceback
os.environ['OMP_NUM_THREADS']='2'
import numpy as np
import torch
from torch import nn
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'residual_throughput_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'session':355735431,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'single free T4 resident-batch forward/backward/zero-lr optimizer timing only','production_training':False,'model_update':False,'paid_spending_usd':0,'deletions':[],'results':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def weights(model):return hashlib.sha256(b''.join(v.detach().cpu().numpy().tobytes() for v in model.parameters())).hexdigest()
def save(s):m['stage']=s;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(s,flush=True)
try:
 save('loading native prefix to one free GPU; unchanged model timing')
 assert torch.cuda.is_available();torch.set_num_threads(2);torch.manual_seed(12606);device='cuda:0';m['gpu']=torch.cuda.get_device_name(0);m['capability']=list(torch.cuda.get_device_capability(0));m['torch_version']=torch.__version__;m['native_bf16_supported']=torch.cuda.is_bf16_supported(including_emulation=False);m['dtype']='float32';m['batch_useful_bit_targets']=32768
 t=time.monotonic();count=32768;p=np.fromfile(R/'atom_cache_v1/a_native/final_p.u16',dtype='<u2',count=count).astype(np.float64);raw=(R/'atom_cache_v1/a512k.bin').read_bytes()[:4096];y=((np.frombuffer(raw,np.uint8)[:,None]>>(7-np.arange(8)))&1).astype(np.float32).reshape(-1);f=np.memmap(R/'native_stage_trace_v1/a512k/stage.f32',dtype='<f4',mode='r',offset=12,shape=(4194304,19));x=np.zeros((count,24),np.float32);x[:,:14]=np.clip(f[:count,:14],-12,12)/12;ell=np.log(p/(65536-p))
 for j,k in enumerate([14,18,17]):prob=np.clip(f[:count,k].astype(np.float64),1/65536,65535/65536);x[:,14+j]=np.clip(np.log(prob/(1-prob))-ell,-12,12)/12
 x[:,17]=4*(p/65536)*(1-p/65536);x[:,18]=(np.arange(count)%8)/7
 x=torch.as_tensor(x,device=device);target=torch.as_tensor(y,device=device);offset=torch.as_tensor(ell.astype(np.float32),device=device);torch.cuda.synchronize();m['preload_wall_seconds']=time.monotonic()-t
 class GRU(nn.Module):
  def __init__(self):super().__init__();self.gru=nn.GRU(24,16,batch_first=True);self.head=nn.Linear(16,1)
  def forward(self,x):h,_=self.gru(x.reshape(256,128,24));return self.head(h).reshape(-1)
 for name,model in [('MLP24_32_1',nn.Sequential(nn.Linear(24,32),nn.Tanh(),nn.Linear(32,1))),('GRU24_16_1_seq128',GRU())]:
  model=model.to(device);head=model[-1] if name.startswith('MLP') else model.head;nn.init.zeros_(head.weight);nn.init.zeros_(head.bias);before=weights(model);opt=torch.optim.AdamW(model.parameters(),lr=0);torch.cuda.reset_peak_memory_stats();times=[]
  for j in range(16):
   torch.cuda.synchronize();start=time.monotonic();opt.zero_grad(set_to_none=True);delta=model(x).reshape(-1);loss=nn.functional.binary_cross_entropy_with_logits(offset+delta,target);loss.backward();opt.step();torch.cuda.synchronize();elapsed=time.monotonic()-start
   if j>=4:times.append(elapsed)
  after=weights(model);assert before==after;median=float(np.median(times));row={'name':name,'parameter_count':sum(v.numel() for v in model.parameters()),'warm_steps':4,'timed_steps':12,'median_step_seconds':median,'p90_step_seconds':float(np.quantile(times,.9)),'useful_bit_targets_per_GPU_second':count/median,'peak_device_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_device_reserved_bytes':torch.cuda.max_memory_reserved(),'before_after_parameter_sha256':before,'parameters_unchanged':True,'optimizer_lr':0.,'resident_repeated_batch_not_training_coverage':True};m['results'].append(row);save('timed '+name)
 m['source_hashes']=[{'file':s,'sha256':sha(R/s)} for s in ['research_round8_residual_throughput_worker.py','research_round8_residual_throughput_protocol.md']];m.update(status='COMPLETE_FREE_T4_RESIDUAL_THROUGHPUT_ONLY',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('timing complete; no model updates, no5090extrapolation')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
