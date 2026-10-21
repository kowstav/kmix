import os
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2';os.environ['MKL_NUM_THREADS']='2'
import ast,datetime,gzip,hashlib,json,pathlib,re,time,traceback
import numpy as np
from scipy.special import expit
import torch
from torch import nn
R=pathlib.Path('/kaggle/working/hp_round8');N=R/'atom_cache_v1';S=R/'native_stage_trace_v1';W=R/'native_stage_weak_confirmation_v1';D=R/'rarity_residual_pilot_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','session':355735431,'pid':os.getpid(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'partial A96 dictionary-atom mask training of a tiny residual; original transformer unchanged','core_retraining':False,'production_training':False,'paid_spending_usd':0,'deletions':[],'rungs':[],'confirmation':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(s):
 m['stage']=s;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(s,flush=True)
try:
 torch.set_num_threads(2);assert torch.cuda.is_available();device='cuda:0';m['gpu']=torch.cuda.get_device_name(0);m['torch_version']=torch.__version__;m['source_hashes']=[{'file':n,'sha256':sha(R/n)} for n in ['research_round8_rarity_residual_pilot_worker.py','research_round8_rarity_residual_pilot_protocol.md']]
 native=json.loads((N/'manifest.json').read_text());stage=json.loads((S/'manifest.json').read_text());weak=json.loads((W/'manifest.json').read_text());wide=json.loads((R/'source_wide_box_v1/manifest.json').read_text());census=json.loads((R/'rarity_census_v1/manifest.json').read_text())
 assert wide['status']=='COMPLETE_WIDER_SOURCE_FINITE_BOX' and census['status']=='COMPLETE_RARITY_CENSUS_DIAGNOSTIC';m['frozen_offset_coefficients']=wide['coefficients'];theta=np.array(wide['coefficients']);dictionary=R/'native_hidden_trace_v1/tree/dictionary/english.dic';assert sha(dictionary)==native['dictionary_sha256'];words=re.findall('[a-z]+',dictionary.read_text());assert len(words)==44515
 # Reuse only parser definitions, never execute the parent's experiment module.
 nodes=ast.parse((R/'research_round8_native_stage_fit_worker_v2.py').read_text());functions=[n for n in nodes.body if isinstance(n,ast.FunctionDef) and n.name in ['inv','wordcode','dictionary_index']];assert len(functions)==3;ns={};exec(compile(ast.Module(body=functions,type_ignores=[]),'<verified-v2-word-parser>','exec'),ns);inv=ns['inv'];wordcode=ns['wordcode'];dictionary_index=ns['dictionary_index'];m['parser_source_sha256']=sha(R/'research_round8_native_stage_fit_worker_v2.py')
 for j in range(len(words)):
  code=list(map(inv,wordcode(j)));assert dictionary_index(code)==j
  for k in range(1,len(code)):assert dictionary_index(code[:k]) is None
 m['all_dictionary_code_and_prefix_tests']='PASS';wanted=set(words);counts={}
 fp=R/'rarity_census_v1/word_article_frequencies.tsv.gz';assert sha(fp)==census['frequency_file']['sha256']
 with gzip.open(fp,'rt',encoding='utf-8') as f:
  next(f)
  for line in f:
   w,c,*_=line.rstrip('\n').split('\t')
   if w in wanted:counts[w]=int(c)
 frequency=np.array([counts.get(w,0) for w in words],np.int64);m['dictionary_types_with_census_count']=len(counts);m['count_zero_policy']='dictionary entries absent from census treated as below every cutoff; target policy only'
 marker=b''.join(wordcode(words.index(p)) if p.isalpha() else bytes([inv(ord(p))]) for p in re.findall('[a-z]+|[^a-z]','  <page>\n    <title>'))
 def labels(raw):
  result=np.full(len(raw),-1,np.int64);at=raw.find(marker);assert at>=0;start=at+len(marker);pending=[];escape=False;begin=start;spans=0
  for i in range(start,len(raw)):
   if escape:escape=False;continue
   if not pending:begin=i
   pending.append(inv(raw[i]))
   if pending[0]<128:assert len(pending)==1;escape=pending[0]==12;pending=[];continue
   j=dictionary_index(pending)
   if j is None:continue
   assert 0<=j<len(words);result[begin:i+1]=frequency[j];spans+=1;pending=[]
  return result,{'recognized_page_byte':at,'unaligned_prefix_bytes':start,'dictionary_spans':spans,'dictionary_code_bytes':int(np.sum(result>=0)),'incomplete_terminal_code_bytes':len(pending)}
 def load_slice(s):
  n=next(v for v in native['native_exports'] if v['slice']==s);root=S/(s+'512k') if s in 'ab' else W/(s+'512k');sr=next(v for v in (stage['exports'] if s in 'ab' else weak['exports']) if v['slice']==s);raw=(N/(s+'512k.bin')).read_bytes();assert hashlib.sha256(raw).hexdigest()==n['input_sha256'];pp=N/(s+'_native/final_p.u16');assert sha(pp)==n['final_p_sha256'];sp=root/'stage.f32';assert sha(sp)==sr['stage_sha256'];p=np.fromfile(pp,dtype='<u2').astype(np.float64);ell=np.log(p/(65536-p));h=np.memmap(N/(s+'_native/hidden.q8'),dtype=np.uint8,mode='r',shape=(len(raw),193));valid=np.repeat(np.r_[np.uint8(0),h[:-1,0]],8).astype(np.float32);frames=np.memmap(sp,dtype='<f4',mode='r',offset=12,shape=(len(p),19));x=np.empty((len(p),8),np.float32);x[:,0]=ell/12
  for j,k in enumerate([17,18,14]):
   prob=np.clip(frames[:,k].astype(np.float64),1/65536,65535/65536);x[:,j+1]=(np.clip(np.log(prob/(1-prob))-ell,-12,12)/12).astype(np.float32)
  x[:,1]*=valid;x[:,4]=4*(p/65536)*(1-p/65536);x[:,5]=(np.arange(len(p))%8)/7;x[:,6]=valid;x[:,7]=1;assert np.isfinite(x).all();offset=ell+theta[0]+theta[1]*ell+theta[2]*x[:,1].astype(np.float64);y=((np.frombuffer(raw,np.uint8)[:,None]>>(7-np.arange(8)))&1).astype(np.float32).reshape(-1);f,info=labels(raw);f=np.repeat(f,8);info.update(slice=s,input_sha256=n['input_sha256'],stage_sha256=sr['stage_sha256'],mask_fractions={str(c):float(np.mean((f>=0)&(f<c))) for c in [107,1392,8372]});m.setdefault('slice_alignment',[]).append(info);return {'x':x,'offset':offset,'y':y,'frequency':f,'p':p}
 save('verified dictionary code spans and census; assembling native A/B features')
 data={s:load_slice(s) for s in 'ab'};cut=393216*8
 train={k:np.concatenate([data[s][k][:cut] for s in 'ab']) for k in ['x','offset','y','frequency']};dev={k:np.concatenate([data[s][k][cut:] for s in 'ab']) for k in ['x','offset','y','frequency','p']}
 # Integer-law roundtrip and feature future-noninterference are different gates.
 integers=np.arange(1,65536,dtype=np.float64);assert np.array_equal(np.floor(65536*expit(np.log(integers/(65536-integers)))+.5),integers);m['all_native_Q16_identity_roundtrips']='PASS'
 tx=torch.as_tensor(train['x'],device=device);to=torch.as_tensor(train['offset'].astype(np.float32),device=device);ty=torch.as_tensor(train['y'],device=device);tf=torch.as_tensor(train['frequency'],device=device)
 arms=[{'name':'unweighted','cutoff':None,'rare_weight':1.}]+[{'name':f'cut{c}_weight{w}','cutoff':c,'rare_weight':w} for c in [107,1392,8372] for w in [0.,.25,.5]];seeds=[6106,6107];models={};optimizers={};steps={};pools={};training_time={};batch=32768
 def new_model(seed):
  torch.manual_seed(seed);model=nn.Sequential(nn.Linear(8,16),nn.Tanh(),nn.Linear(16,1)).to(device);nn.init.zeros_(model[-1].weight);nn.init.zeros_(model[-1].bias);return model
 for a in arms:
  rare=torch.zeros(len(tf),dtype=torch.bool,device=device) if a['cutoff'] is None else ((tf>=0)&(tf<a['cutoff']));pools[a['name']]={'rare':rare,'active':torch.where(~rare)[0] if a['rare_weight']==0 else None};assert a['rare_weight']!=0 or len(pools[a['name']]['active'])>0
  for seed in seeds:
   key=(a['name'],seed);model=new_model(seed);models[key]=model;optimizers[key]=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=0);steps[key]=0;training_time[key]=0.
 m.update(parameter_count=161,serialized_parameter_bytes_per_copy=644,batch_nonzero_bit_targets=batch,training_bit_targets=len(tf),development_bit_targets=len(dev['y']),dtype='FP32',learning_rate=.001,weight_decay=0.,training_pool_policy='zero-mask samples active pool; other arms sample all bits; not equal common-target exposure')
 def flat(model):return np.concatenate([v.detach().cpu().numpy().reshape(-1) for v in model.parameters()]).astype('<f4')
 def score(rec,weights,cutoff=None):
  W1=weights[:128].astype(np.float64).reshape(16,8);b1=weights[128:144].astype(np.float64);W2=weights[144:160].astype(np.float64);b2=float(weights[160]);g=extra=rare_g=other_g=0.;qsha=hashlib.sha256();count=0
  for i in range(0,len(rec['y']),131072):
   sl=slice(i,i+131072);y=rec['y'][sl].astype(bool);x=rec['x'][sl].astype(np.float64);delta=np.tanh(x@W1.T+b1)@W2+b2;q=np.clip(np.floor(65536*expit(rec['offset'][sl]+delta)+.5),1,65535).astype('<u2');qsha.update(q.tobytes());old=rec['p'][sl];base=np.clip(np.floor(65536*expit(rec['offset'][sl])+.5),1,65535);chosen=np.where(y,q.astype(np.float64),65536-q.astype(np.float64));bits=np.log2(chosen/np.where(y,old,65536-old))/8;g+=float(bits.sum());extra+=float(np.log2(chosen/np.where(y,base,65536-base)).sum()/8);rare=np.zeros(len(y),bool) if cutoff is None else ((rec['frequency'][sl]>=0)&(rec['frequency'][sl]<cutoff));rare_g+=float(bits[rare].sum());other_g+=float(bits[~rare].sum());count+=int(rare.sum())
  return {'Q16_gain_vs_original_bytes':g,'Q16_gain_vs_wide_bytes':extra,'masked_dictionary_gain_vs_original_bytes':rare_g,'other_gain_vs_original_bytes':other_g,'masked_dictionary_bit_targets':count,'reference_Q16_sha256':qsha.hexdigest()}
 zero=flat(new_model(6106));assert np.all(zero[144:]==0);assert score(dev,zero)['Q16_gain_vs_wide_bytes']==0.;m['zero_residual_reference_identity']='PASS'
 # This MLP has no future read or recurrent carry; challenge complete predicted prefix.
 probe={k:v[:8192].copy() for k,v in dev.items()};changed={k:v.copy() for k,v in probe.items()};changed['x'][4096:]=7;changed['y'][4096:]=1-changed['y'][4096:];changed['offset'][4096:]=12;changed['p'][4096:]=1
 challenge=zero.copy();challenge[144:160]=np.linspace(-.1,.1,16);challenge[160]=.02
 assert score({k:v[:4096] for k,v in probe.items()},challenge)['reference_Q16_sha256']==score({k:v[:4096] for k,v in changed.items()},challenge)['reference_Q16_sha256'];m['future_feature_target_integer_prefix_identity']='PASS'
 def gradients(model,a):
  c=a['cutoff'] or 1392;rare=(tf[:32768]>=0)&(tf[:32768]<c);common=~rare;out=[]
  for mask in [common,rare]:
   if not int(mask.sum()):return {'status':'one_class_empty','cutoff':c}
   pred=to[:32768]+model(tx[:32768]).reshape(-1);loss=nn.functional.binary_cross_entropy_with_logits(pred[mask],ty[:32768][mask]);v=torch.autograd.grad(loss,tuple(model.parameters()));out.append(torch.cat([z.reshape(-1) for z in v]).detach().cpu().numpy().astype(np.float64))
  gc,gr=out;dot=float(gc@gr);nc=float(np.linalg.norm(gc));nr=float(np.linalg.norm(gr));return {'cutoff':c,'common_targets':int(common.sum()),'rare_targets':int(rare.sum()),'common_norm':nc,'rare_norm':nr,'dot_product':dot,'cosine':dot/(nc*nr) if nc*nr else None,'scope':'tiny residual parameters only, not original transformer'}
 m['initial_gradient_geometry']=gradients(models[('unweighted',6106)],arms[0]);save('all masks fixed; training first128steps on free T4')
 survivors=[a['name'] for a in arms];byname={a['name']:a for a in arms}
 for rung in [128,384,1152]:
  for name in survivors:
   a=byname[name];pool=pools[name]
   for seed in seeds:
    key=(name,seed);model=models[key];opt=optimizers[key];generator=torch.Generator(device=device);generator.manual_seed(seed+steps[key]*101);torch.cuda.synchronize();t=time.monotonic()
    while steps[key]<rung:
     active=pool['active'];idx=torch.randint(len(tf) if active is None else len(active),(batch,),generator=generator,device=device);idx=idx if active is None else active[idx];weight=torch.where(pool['rare'][idx],a['rare_weight'],1.);opt.zero_grad(set_to_none=True);loss=(nn.functional.binary_cross_entropy_with_logits(to[idx]+model(tx[idx]).reshape(-1),ty[idx],reduction='none')*weight).sum()/weight.sum();loss.backward();opt.step();steps[key]+=1
    torch.cuda.synchronize();training_time[key]+=time.monotonic()-t;weights=flat(model);wp=D/f'{name}_seed{seed}_step{rung}.f32';wp.write_bytes(weights.tobytes());resume=wp.with_suffix('.resume.pt');torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'steps':rung,'seed':seed,'arm':a,'next_rung_sampler_seed':seed+rung*101},resume);result=score(dev,weights,a['cutoff']);m['rungs'].append({'arm':name,'seed':seed,'step':rung,'training_seconds':training_time[key],'sampled_nonzero_loss_bit_targets':rung*batch,'inspected_sampled_bit_targets':rung*batch,'pool_nonzero_fraction':float(len(active)/len(tf)) if active is not None else 1.,'active_pool_sampling_not_same_common_exposure':True,'parameter_file':wp.name,'parameter_bytes':wp.stat().st_size,'parameter_sha256':sha(wp),'optimizer_resume_file':resume.name,'optimizer_resume_sha256':sha(resume),'development':result});save(f'completed {name} seed{seed} step{rung}')
  ranking=sorted([name for name in survivors if name!='unweighted'],key=lambda name:np.mean([v['development']['Q16_gain_vs_wide_bytes'] for v in m['rungs'] if v['arm']==name and v['step']==rung]),reverse=True)
  if rung<1152:survivors=['unweighted']+ranking[:4 if rung==128 else 2];m.setdefault('locked_rung_selections',[]).append({'after_step':rung,'next_arms':survivors.copy()});save('development-only selection locked')
 m['finalists_frozen_before_confirmation']=survivors.copy();m['final_gradient_geometry']=[{'arm':name,**gradients(models[(name,6106)],byname[name])} for name in survivors];save('finalists frozen; loading held-out C/D for first scoring in this fit')
 for s in 'cd':
  rec=load_slice(s)
  for name in survivors:
   for seed in seeds:
    key=(name,seed);m['confirmation'].append({'slice':s,'arm':name,'seed':seed,'step':steps[key],'result':score(rec,flat(models[key]),byname[name]['cutoff'])});save('confirmation '+s+' '+name+' seed'+str(seed))
  del rec
 m['priced_confirmation']=[]
 for name in survivors:
  for seed in seeds:
   values=[v['result'] for v in m['confirmation'] if v['arm']==name and v['seed']==seed];gain=sum(v['Q16_gain_vs_original_bytes'] for v in values);extra=sum(v['Q16_gain_vs_wide_bytes'] for v in values);m['priced_confirmation'].append({'arm':name,'seed':seed,'CD_gain_vs_original_bytes':gain,'CD_gain_vs_wide_bytes':extra,'two_parameter_copy_bytes':1288,'selector_bytes':.625,'CD_after_parameters_selector_bytes':gain-1288-.625,'both_slices_improve_vs_original':all(v['Q16_gain_vs_original_bytes']>0 for v in values),'both_slices_improve_vs_wide':all(v['Q16_gain_vs_wide_bytes']>0 for v in values)})
 # Quantify implementation discrepancy, never silently call GPU and reference identical.
 model=models[('unweighted',6106)];weights=flat(model);rec={k:v[:32768] for k,v in dev.items()};xf=torch.as_tensor(rec['x'],device=device);of=torch.as_tensor(rec['offset'].astype(np.float32),device=device)
 with torch.no_grad():z=(of+model(xf).reshape(-1)).cpu().numpy().astype(np.float64)
 W1=weights[:128].astype(np.float64).reshape(16,8);b1=weights[128:144].astype(np.float64);W2=weights[144:160].astype(np.float64);zref=rec['offset']+np.tanh(rec['x'].astype(np.float64)@W1.T+b1)@W2+float(weights[160]);u=np.clip(np.floor(65536*expit(z)+.5),1,65535);v=np.clip(np.floor(65536*expit(zref)+.5),1,65535);m['GPU_reference_comparison']={'targets':len(z),'max_abs_logit_difference':float(np.max(np.abs(z-zref))),'Q16_unequal_events':int(np.sum(u!=v)),'native_reference_implementation':'saved FP32 parameters, FP64 inference; native integration unexecuted'}
 m.update(status='COMPLETE_PARTIAL_DICTIONARY_MASK_RESIDUAL_TRAINING',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_candidate_archive_evaluated=False,original_transformer_gradient_interference_measured=False,all_word_mask_training_completed=False,peak_device_allocated_bytes=torch.cuda.max_memory_allocated());save('partial free-T4 mask pilot complete; core/OOV/native qualification open')
except BaseException as e:
 m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved before any named repair');raise
