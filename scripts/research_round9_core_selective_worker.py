"""Actual input redaction and projection of Adam's actual proposed update.

Wait for exact native regenerated priors, then import the actual selected core.
All arms share examples by seed. Frequency labels enter only loss supervision;
redacted-input decoding requires the priced constants stream already tested.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='1';os.environ['OMP_NUM_THREADS']='2'
import pathlib,json,time,hashlib,traceback,ast,math,copy
R=pathlib.Path('/kaggle/working/hp_round9');M=R/'core_selective_v1';M.mkdir(exist_ok=False)
status={'status':'WAITING_FOR_DISTRIBUTED_NATIVE_INPUTS','pid':os.getpid(),'started':time.time(),'stage':'waiting without using GPU; reuse existing data job','spending_usd':0,'deletions':[]};(M/'manifest.json').write_text(json.dumps(status,indent=2))
try:
 start=time.time()
 while True:
  p=R/'distributed_core_data_v1/manifest.json'
  if p.exists():
   distributed_ready=json.loads(p.read_text())
   if distributed_ready['status'].startswith('COMPLETE'):break
   if distributed_ready['status']=='FAIL':raise RuntimeError(distributed_ready['error'])
  assert time.time()-start<10800,'native distributed input preparation exceeded3hours';time.sleep(10)
 source=R/'research_round9_core_training_worker_v2.py';text=source.read_text().replace("CUDA_VISIBLE_DEVICES']='0'","CUDA_VISIBLE_DEVICES']='1'").replace("D=R/'core_training_v2'","D=pathlib.Path('/root/hp_round9/core_selective_v1')").replace("(D/'manifest.json').write_text(json.dumps(m,indent=2))","(D/'manifest.json').write_text(json.dumps(m,indent=2));(M/'manifest.json').write_text(json.dumps(m,indent=2))")
 tree=ast.parse(text);selected=[];found=False
 for node in tree.body:
  if isinstance(node,ast.Try):
   for stmt in node.body:
    if isinstance(stmt,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='tokens' for t in stmt.targets):found=True;break
    selected.append(stmt)
   break
  selected.append(node)
 assert found;exec(compile(ast.Module(body=selected,type_ignores=[]),'<actual-core-import-only>','exec'),globals())
 m.update(scope='same original core; selective parameter updates and native-code-cell change penalty, paired controls; not a measured compressed-rate regularizer',rungs=[],projection_geometry=[],confirmation=[],setup_source_sha256=sha(source),worker_sha256=sha(R/'research_round9_distributed_core_training_v2_worker.py'),scratch=str(D),native_likelihood_parity_resolved=False)
 data={}
 for row in distributed_ready['slices']:
  root=pathlib.Path(row['files'][0]['path']).parent;tokens=np.fromfile(root/'tokens.u8','u1').astype(np.int64);fr=np.fromfile(root/'word_frequency.i32','<i4');pr=np.memmap(root/'priors.f16','<f2','r',shape=(len(tokens),205));bd=np.fromfile(root/'bounds.i32','<i4');articles=[(int(a),int(b)) for a,b in zip(bd[:-1],bd[1:]) if b-a>=65];data[(row['slice'],row['mode'])]={'tokens':tokens,'freq':fr,'prior':pr,'articles':articles}
 def forward(rec,lo,hi):
  x=torch.tensor(rec['tokens'][lo:hi],device='cuda')[None];pr=torch.tensor(np.asarray(rec['prior'][lo:hi],np.float32),device='cuda')[None];cu=torch.tensor([[0,hi-lo]],dtype=torch.int32,device='cuda');return model.compute_logits(x,pr,cu)[0].float()
 def evaluate(mode,slices):
  model.eval();total=common=rare=0.;nt=nc=nr=0
  with torch.no_grad():
   for s in slices:
    rec=data[(s,mode)]
    for a,b in rec['articles']:
     b=min(b,a+1024);z=forward(rec,a,b)[:-1];target=torch.tensor(rec['tokens'][a+1:b],device='cuda');loss=F.cross_entropy(z,target,reduction='none').cpu().numpy()/math.log(2);fr=rec['freq'][a+1:b];rm=(fr>=0)&(fr<1392);total+=float(loss.sum());nt+=len(loss);common+=float(loss[~rm].sum());nc+=int((~rm).sum());rare+=float(loss[rm].sum());nr+=int(rm.sum())
  return {'all_bits_per_symbol':total/nt,'common_or_unlabelled_bits_per_symbol':common/nc,'rare_or_redacted_bits_per_symbol':rare/max(1,nr),'targets':nt,'common_targets':nc,'rare_targets':nr,'mode':mode,'slices':slices}
 initial=copy.deepcopy(model.state_dict())
 arms=[{'name':'unembedding_high','mode':'raw','lambda':1.,'group':'unembedding','lr':1e-4}, {'name':'recurrent_gates_high','mode':'raw','lambda':1.,'group':'recurrent','lr':1e-4}, {'name':'last_block_high','mode':'raw','lambda':1.,'group':'last_block','lr':1e-4}, {'name':'all_high_control','mode':'raw','lambda':1.,'group':'all','lr':3e-5}, {'name':'all_high_codecell','mode':'raw','lambda':1.,'group':'all','lr':3e-5,'cell_penalty':.01}, {'name':'all_high_halfmask_codecell','mode':'raw','lambda':.5,'group':'all','lr':3e-5,'cell_penalty':.01}]
 m['contract']={'arms':arms,'seeds':[7006,7007],'rungs':[128,384],'train':'same A/B article/sample plan as core_distributed_v2; native raw priors, true reset prefix through4096,last256targets','development':'C/D full original-symbol cost,common,rare','confirmation':'E/F core-fit-held-out previously seen by other branches; evaluate all without selecting on E/F','rate_penalty':'lambda .01 times mean squared excess displacement beyond .49*minimum learned native code-level spacing,normalized by that spacing; this proxies code flips and does not measure compressed bits','model_price':'must export native tensors, count changed bytes, pack exact model and compare actual archives; no package gain is inferred from penalty or GPU CE','group_controls':'higher learning-rate all-core control vs exactly same lr/plan code-cell penalty; selective groups measure frozen native weights, not extra parameter capacity','native_fidelity':'GPU/native unresolved; actual native codec validation required','optimizer':'AdamW,wd0,clip1,foreachFalse'}
 cell_refs=[]
 for name,param in model.named_parameters():
  if name+'.q' not in tensors:continue
  scale=tensors[name+'.scale'].reshape(-1,1)
  cb=tensors.get(name+'.codebook')
  step_size=scale*(float((cb[1:]-cb[:-1]).abs().min())*.25 if cb is not None else 1.)
  cell_refs.append((name,param,initial[name].detach(),step_size.clamp_min(1e-12)))
 def select_group(name,group):
  if group=='all':return True
  if group=='unembedding':return name.startswith('unembedding.')
  if group=='last_block':return name.startswith('blocks.11.')
  if group=='recurrent':return any(key in name for key in ['beta_projection','log_baseline_decay_rate','dt_bias','forget_gate_projection','output_gate_projection'])
  raise ValueError(group)
 m['parameter_groups']=[]
 m['baselines']={'raw':evaluate('raw','cd')};m['zero_EF']=evaluate('raw','ef');save('distributed raw/redacted zero-update baseline measured')
 for seed in [7006,7007]:
  plan=[(s,a,b) for s in 'ab' for a,b in data[(s,'raw')]['articles']]
  for arm in arms:
   model.load_state_dict(initial)
   for name,param in model.named_parameters():param.requires_grad_(select_group(name,arm['group']))
   trainable=tuple(p for p in model.parameters() if p.requires_grad);m['parameter_groups'].append({'arm':arm['name'],'seed':seed,'trainable_scalars':sum(p.numel() for p in trainable),'trainable_names':[name for name,p in model.named_parameters() if p.requires_grad]})
   opt=torch.optim.AdamW(trainable,lr=arm['lr'],weight_decay=0);rng=np.random.default_rng(seed);model.train();start=time.monotonic();targets=0
   for step in range(1,385):
    s,a,b=plan[int(rng.integers(len(plan)))];rec=data[(s,arm['mode'])];hi=int(rng.integers(a+65,min(b,a+4096)+1));lo=max(a+1,hi-256);z=forward(rec,a,hi)[lo-a-1:-1];target=torch.tensor(rec['tokens'][lo:hi],device='cuda');fr=torch.tensor(rec['freq'][lo:hi],device='cuda');rare=(fr>=0)&(fr<1392);losses=F.cross_entropy(z,target,reduction='none');w=torch.where(rare,arm['lambda'],1.);opt.zero_grad(set_to_none=True);parameters=trainable;gc=None
    if arm.get('project_actual') and bool((~rare).any()):gc=torch.autograd.grad((losses*(~rare)).mean(),parameters,retain_graph=True);old=[p.detach().clone() for p in parameters]
    objective=(losses*w).sum().div(w.sum().clamp_min(1))
    if arm.get('cell_penalty'):
     terms=[((p-ref).abs().div(spacing).sub(.49).relu().square()).mean() for name,p,ref,spacing in cell_refs if p.requires_grad];penalty=torch.stack(terms).mean();objective=objective+arm['cell_penalty']*penalty
    objective.backward();torch.nn.utils.clip_grad_norm_(parameters,1.);opt.step()
    if gc is not None:
     with torch.no_grad():
      lr=opt.param_groups[0]['lr'];dot=sum((g*(v-p)).sum() for g,v,p in zip(gc,old,parameters));nc=sum((g*g).sum() for g in gc);coef=torch.minimum(dot,torch.zeros_like(dot))/nc.clamp_min(1e-20)
      for p,g in zip(parameters,gc):p.add_(coef*g)
      if step in [1,32,128,384]:
       after=sum((g*(v-p)).sum() for g,v,p in zip(gc,old,parameters));m['projection_geometry'].append({'seed':seed,'step':step,'common_gradient_dot_actual_displacement_before':float(dot),'after':float(after),'projected':bool(dot<0),'rounding_tolerance':'shadow float32, projection changes can round; finite-step/native quantized loss is not guaranteed'})
    targets+=len(target)
    if step%64==0:save(arm['name']+' seed'+str(seed)+' step'+str(step))
    if step in [128,384]:
     assert all(torch.equal(p.detach(),initial[name]) for name,p in model.named_parameters() if not p.requires_grad),'frozen parameter changed'
     result=evaluate(arm['mode'],'cd');path=D/(arm['name']+'_seed'+str(seed)+'_step'+str(step)+'.pt');torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'step':step,'arm':arm,'seed':seed,'rng':rng.bit_generator.state},path);m['rungs'].append({'arm':arm['name'],'seed':seed,'step':step,'processed_targets':targets,'training_seconds':time.monotonic()-start,'development':result,'checkpoint_path':str(path),'checkpoint_sha256':sha(path)});save('distributed '+arm['name']+' rung complete');model.train()
   result=evaluate(arm['mode'],'ef');m['confirmation'].append({'arm':arm['name'],'seed':seed,'step':384,'mode':arm['mode'],'result':result});save('distributed '+arm['name']+' E/F confirmation')
 m.update(status='COMPLETE_SELECTIVE_CORE_AND_CODE_CELL_UPDATE_SCREEN',finished=time.time(),native_or_full_package_qualified=False,peak_cuda_bytes=torch.cuda.max_memory_allocated());save('selective core paired controls complete; native tensor rate/codec qualification required')
except BaseException as e:
 v=globals().get('m',status);v.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());(M/'manifest.json').write_text(json.dumps(v,indent=2));print(v['traceback'],flush=True);raise
