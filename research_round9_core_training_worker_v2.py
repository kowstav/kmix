"""Actual selected lexical transformer import, full-word loss masks and SGD.

GPU/native likelihood fidelity is measured before SGD. Any discrepancy leaves
all GPU training results diagnostic until repaired and exported natively.
"""
import os,sys
os.environ['CUDA_VISIBLE_DEVICES']='0';os.environ['OMP_NUM_THREADS']='2'
import pathlib,json,time,traceback,struct,hashlib,copy,math
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'core_training_v2';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/core_data_v2');m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scope':'actual12layer192width selected lexical core QAT import, loss-only full literal/OOV masking; not qualified native archive','spending_usd':0,'deletions':[],'rungs':[]}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 ready=json.loads((R/'full_word_alignment_v2/manifest.json').read_text());assert ready['status']=='COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS'
 sys.path.insert(0,'/root/hp_round9/runtime_site_v1');sys.path.insert(0,'/root/hp_round9/restored/src/fx2-cmix-transformer-v1');sys.path.insert(0,str(R))
 import research_round9_tfh as tfh
 torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.manual_seed(6306);m['gpu']=torch.cuda.get_device_name(0)
 f=(S/'lex_weights.bin').open('rb');assert f.read(8)==b'FX2TFW01';n=struct.unpack('<I',f.read(4))[0];tensors={}
 for _ in range(n):
  name=f.read(struct.unpack('<I',f.read(4))[0]).decode();dt=f.read(1)[0];nd=struct.unpack('<I',f.read(4))[0];shape=struct.unpack('<'+'I'*nd,f.read(4*nd));arr=np.frombuffer(f.read(int(np.prod(shape))*[1,2,4,4][dt]),['i1','<u2','<f4','<i4'][dt]).reshape(shape).copy()
  if dt==1:arr=(arr.astype(np.uint32)<<16).view(np.float32)
  tensors[name]=torch.from_numpy(arr).cuda()
 assert tensors['config.actq_dynamic_mm'].item()==1 and tensors['config.codebook_grid'].item()==.25
 class WeightQuant(nn.Module):
  def __init__(self,q,scale,cb=None):
   super().__init__();self.register_buffer('scale',scale.reshape(-1,1));self.register_buffer('cb',cb if cb is not None else torch.arange(-127,128,dtype=torch.float32,device='cuda'));self.grid=.25 if cb is not None else 1.
  def forward(self,w,**kwargs):
   normalized=w/(self.scale*self.grid);levels=self.cb
   # Sorted nearest levels without materializing W*15 or W*255 differences.
   ix=torch.searchsorted(levels.contiguous(),normalized.contiguous());lo=(ix-1).clamp(0,len(levels)-1);hi=ix.clamp(0,len(levels)-1);nearest=torch.where((normalized-levels[lo]).abs()<=(normalized-levels[hi]).abs(),levels[lo],levels[hi]);q=nearest*self.scale*self.grid;return w+(q-w).detach()
 class DynamicAct(nn.Module):
  def forward(self,x,**kwargs):
   scale=x.abs().amax(-1,keepdim=True).clamp_min(1e-12)/127.;q=torch.round(x/scale).clamp(-128,127)*scale;return x+(q-x).detach()
 class StaticAct(nn.Module):
  def __init__(self,scale):super().__init__();self.register_buffer('scale',scale.reshape(-1,1))
  def forward(self,x,**kwargs):q=torch.round(x/self.scale).clamp(-128,127)*self.scale;return x+(q-x).detach()
 model=tfh.Transformer(tfh.make_config(quantized=False)).cuda();params=dict(model.named_parameters());loaded=[]
 with torch.no_grad():
  for name,param in params.items():
   if name in tensors:param.copy_(tensors[name].reshape(param.shape));loaded.append(name)
   elif name+'.q' in tensors:
    q=tensors[name+'.q'].long();scale=tensors[name+'.scale'].reshape(-1,1);cb=tensors.get(name+'.codebook');deq=(cb[q+7].float()*.25 if cb is not None else q.float())*scale;param.copy_(deq);loaded.append(name)
   else:raise RuntimeError('missing actual selected-model parameter '+name)
 for name,module in list(model.named_modules()):
  if hasattr(module,'quantize_weight') and name+'.weight.q' in tensors:
   module.quantize_weight=WeightQuant(tensors[name+'.weight.q'],tensors[name+'.weight.scale'],tensors.get(name+'.weight.codebook'))
   if hasattr(module,'quantize_activation'):module.quantize_activation=DynamicAct()
  for attr in ['quantize_queries','quantize_keys','quantize_values']:
   key=name+'.'+attr+'.scale'
   if key in tensors:setattr(module,attr,StaticAct(tensors[key]))
 # Original cfg tests qkv_quantization before applying modules; activate it.
 from dataclasses import replace
 cfg=replace(model.cfg,qkv_quantization=tfh.Quantization(buckets=256,block_size=None,scale_dtype=torch.bfloat16,arithmetic_dtype=torch.float32,scale_init='scaled_mean',epsilon=None))
 for module in model.modules():
  if hasattr(module,'cfg'):module.cfg=cfg
 m['actual_core_import']={'loaded_parameters':len(loaded),'parameter_count':sum(p.numel() for p in params.values()),'packed_source_sha256':sha(pathlib.Path('/kaggle/working/hp_round7/lex_audit/lex_h1_run11.tfwc2')),'imported_tensors_sha256':sha(S/'lex_weights.bin'),'weight_laws':'learned15level codebooks on0.25grid plus8bit small tables; fixed native BF16 row scales, STE nearest native code levels','activation_laws':'dynamic per-token amax/127, static per-head QKV scales','state':'FLa parallel KDA and T4 sliding-window SDPA; native equivalence measured below, not presumed'}
 tokens=np.fromfile(S/'tokens.u8','u1').astype(np.int64);freq=np.fromfile(S/'word_frequency.i32','<i4');prior=np.memmap(S/'priors.f16','<f2','r',shape=(len(tokens),205));native=np.memmap(S/'native_nn.f16','<f2','r',shape=(len(tokens),205));bounds=np.fromfile(S/'bounds.i32','<i4');assert len(freq)==len(tokens)
 def forward(lo,hi):
  x=torch.tensor(tokens[lo:hi],device='cuda')[None];pr=torch.tensor(np.asarray(prior[lo:hi],np.float32),device='cuda')[None];cu=torch.tensor([[0,hi-lo]],dtype=torch.int32,device='cuda');return model.compute_logits(x,pr,cu)[0].float()
 save('actual selected core imported; measuring zero-update native likelihood fidelity')
 model.eval();parity=[]
 with torch.no_grad():
  for lo,hi in list(zip(bounds[:-1],bounds[1:]))[:16]:
   lo=int(lo);hi=min(int(hi),lo+4096)
   if hi-lo<2:continue
   q=forward(lo,hi).softmax(-1).cpu().numpy().astype(np.float64)[:-1];p=np.maximum(np.asarray(native[lo:hi-1],np.float64),1e-6);p/=p.sum(-1,keepdims=True);q=np.maximum(q,1e-6);q/=q.sum(-1,keepdims=True);target=tokens[lo+1:hi];dif=np.log2(q[np.arange(len(q)),target]/p[np.arange(len(p)),target]);parity.append({'start':lo,'rows':len(q),'mean_absolute_target_bits_difference':float(np.abs(dif).mean()),'max_absolute_target_bits_difference':float(np.abs(dif).max()),'mean_native_to_GPU_KL_bits':float(np.sum(p*np.log2(p/q),-1).mean()),'max_probability_difference':float(np.max(np.abs(p-q)))})
 m['zero_update_likelihood_parity']=parity;m['native_export_bitexact_passed']=False;m['diagnostic_training_only']=True;save('zero-update likelihood measured; diagnostic original-core SGD begins with unresolved native-export gate')
 initial=copy.deepcopy(model.state_dict());torch.save({'model':initial,'source':'actual imported lexical packed model, not old reference checkpoint'},D/'selected_core_zero_update.pt')
 # Article-level train/development split prevents overlapping article contexts.
 articles=[(int(a),int(b)) for a,b in zip(bounds[:-1],bounds[1:]) if b-a>=65];dev=articles[::5];train=[v for i,v in enumerate(articles) if i%5];m['data_split']={'complete_articles':len(articles),'train_articles':len(train),'development_articles':len(dev),'corpus_scope_bytes':len(tokens),'training_loss_max_tokens':256,'training_context':'sampled prefix through4096tokens from true decoded article reset; last256targets only','all_word_mask_includes_literal_OOV_case_controls':True,'word_mask_input_leakage':False,'mask_changes':'loss weights only; original tokens, priors and rare context remain visible'}
 def evaluate():
  model.eval();losses=[];common=[];rare=[]
  with torch.no_grad():
   for a,b in dev:
    b=min(b,a+1024);z=forward(a,b)[:-1];target=torch.tensor(tokens[a+1:b],device='cuda');l=F.cross_entropy(z,target,reduction='none').cpu().numpy()/math.log(2);fr=freq[a+1:b];losses.extend(l);common.extend(l[(fr<0)|(fr>=1392)]);rare.extend(l[(fr>=0)&(fr<1392)])
  return {'all_bits_per_symbol':float(np.mean(losses)),'common_or_unlabelled_bits_per_symbol':float(np.mean(common)),'rare_bits_per_symbol':float(np.mean(rare)),'targets':len(losses)}
 base=evaluate();m['development_zero_update']=base;save('baseline full-loss evaluation complete')
 arms=[{'name':'unweighted','cutoff':0,'rare_weight':1.},{'name':'cut107_half','cutoff':107,'rare_weight':.5},{'name':'cut1392_half','cutoff':1392,'rare_weight':.5},{'name':'cut1392_zero','cutoff':1392,'rare_weight':0.},{'name':'cut8372_half','cutoff':8372,'rare_weight':.5}]
 for arm in arms:
  model.load_state_dict(initial);opt=torch.optim.AdamW(model.parameters(),lr=1e-5,weight_decay=0);rng=np.random.default_rng(6306);model.train();t=time.monotonic();weight_sum=target_count=0
  for step in range(1,129):
   a,b=train[int(rng.integers(len(train)))];hi=int(rng.integers(a+65,min(b,a+4096)+1));target_lo=max(a+1,hi-256);z=forward(a,hi)[target_lo-a-1:-1];target=torch.tensor(tokens[target_lo:hi],device='cuda');fr=torch.tensor(freq[target_lo:hi],device='cuda');w=torch.where((fr>=0)&(fr<arm['cutoff']),arm['rare_weight'],1.);opt.zero_grad(set_to_none=True);loss=(F.cross_entropy(z,target,reduction='none')*w).sum()/w.sum().clamp_min(1);loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();weight_sum+=float(w.sum());target_count+=len(w)
   if step%16==0:save(arm['name']+' step'+str(step))
   if step in [32,128]:
    result=evaluate();path=D/(arm['name']+'_step'+str(step)+'.pt');torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'step':step,'arm':arm,'rng':rng.bit_generator.state},path);m['rungs'].append({'arm':arm['name'],'step':step,'training_seconds':time.monotonic()-t,'processed_targets':target_count,'sum_loss_weights':weight_sum,'development':result,'checkpoint_sha256':sha(path)});save(arm['name']+' rung'+str(step)+' complete');model.train()
 m.update(status='COMPLETE_ACTUAL_SELECTED_CORE_DIAGNOSTIC_MASK_FINETUNING',finished=time.time(),peak_cuda_bytes=torch.cuda.max_memory_allocated(),native_candidate_archive=False,all96_exhausted=False);save('five actual selected-core full literal/OOV loss-mask arms complete; native qualification remains open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise

