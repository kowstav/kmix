"""Longer two-seed selected-core masking and gradient-projection experiments.

Reuses the executed selected-core import and evaluation definitions through AST
selection. Does not execute the parent's training loop or overwrite its files.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='1';os.environ['OMP_NUM_THREADS']='2'
import pathlib,ast,hashlib,json,time,traceback,math
R=pathlib.Path('/kaggle/working/hp_round9');M=R/'core_extension_v1';M.mkdir(exist_ok=False)
source=R/'research_round9_core_training_worker_v2.py';text=source.read_text();expected=hashlib.sha256(text.encode()).hexdigest()
text=text.replace("os.environ['CUDA_VISIBLE_DEVICES']='0'","os.environ['CUDA_VISIBLE_DEVICES']='1'").replace("D=R/'core_training_v2'","D=pathlib.Path('/root/hp_round9/core_extension_v1')")
text=text.replace("(D/'manifest.json').write_text(json.dumps(m,indent=2))","(D/'manifest.json').write_text(json.dumps(m,indent=2));(M/'manifest.json').write_text(json.dumps(m,indent=2))")
module=ast.parse(text);selected=[];found=False
for node in module.body:
 if isinstance(node,ast.Try):
  body=[]
  for stmt in node.body:
   if isinstance(stmt,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='arms' for t in stmt.targets):found=True;break
   body.append(stmt)
  selected.extend(body);break
 selected.append(node)
assert found
try:
 exec(compile(ast.Module(body=selected,type_ignores=[]),'<preserved-core-v2-setup>', 'exec'),globals())
 m.update(scope='actual selected-core two-seed longer full-word masking plus gradient-projection descendants; GPU/native parity unresolved',setup_source_sha256=expected,worker_sha256=hashlib.sha256((R/'research_round9_core_extension_worker.py').read_bytes()).hexdigest(),rungs=[],gradient_geometry=[],architecture_extension=False)
 # All arms share the same sampled decoder-reachable article prefixes per seed.
 arms=[{'name':'unweighted','cutoff':0,'lambda':1.},{'name':'cut107_half','cutoff':107,'lambda':.5},{'name':'cut1392_half','cutoff':1392,'lambda':.5},{'name':'cut1392_zero','cutoff':1392,'lambda':0.},{'name':'cut8372_half','cutoff':8372,'lambda':.5},{'name':'projected1392','cutoff':1392,'lambda':1.,'projection':True}]
 m['extended_contract']={'seeds':[6506,6507],'rungs':[128,384,1152],'learning_rate':1e-5,'train_context':'true article prefix through4096tokens, last256target loss','sample_target_count':'matched identical examples within each seed across every mask','loss_mask_scope':'all decoded whole-word literal/OOV/dictionary/case spans; metadata and whitespace unmasked','projection':'Euclidean rare-gradient projection when its dot with common gradient is negative; first-order common-loss condition, not total-loss guarantee','checkpoint_location':str(D),'paid_compute_usd':0,'native_qualification':'open; GPU finite pilots only','new_dataset_generalization':'same prefix corpus; new distributed corpus slices required before promotion'}
 saves=[];save('two-seed longer masks and shared-core gradient projection starting')
 for seed in [6506,6507]:
  for arm in arms:
   model.load_state_dict(initial);opt=torch.optim.AdamW(model.parameters(),lr=1e-5,weight_decay=0);rng=np.random.default_rng(seed);model.train();t=time.monotonic();targets=0;weights=0.
   for step in range(1,1153):
    a,b=train[int(rng.integers(len(train)))];hi=int(rng.integers(a+65,min(b,a+4096)+1));lo=max(a+1,hi-256);z=forward(a,hi)[lo-a-1:-1];target=torch.tensor(tokens[lo:hi],device='cuda');fr=torch.tensor(freq[lo:hi],device='cuda');rare=(fr>=0)&(fr<arm['cutoff']);losses=F.cross_entropy(z,target,reduction='none');w=torch.where(rare,arm['lambda'],1.);opt.zero_grad(set_to_none=True)
    if arm.get('projection') and bool(rare.any()) and bool((~rare).any()):
     parameters=tuple(model.parameters());gc=torch.autograd.grad((losses*(~rare)).mean(),parameters,retain_graph=True);gr=torch.autograd.grad((losses*rare).mean(),parameters);dot=sum((c*r).sum() for c,r in zip(gc,gr));nc=sum((c*c).sum() for c in gc);nr=sum((r*r).sum() for r in gr);scale=torch.minimum(dot,torch.zeros_like(dot))/nc.clamp_min(1e-20)
     for p,c,r in zip(parameters,gc,gr):p.grad=c+r-scale*c
     if step in [1,32,128,384,1152]:m['gradient_geometry'].append({'arm':arm['name'],'seed':seed,'step':step,'common_count':int((~rare).sum()),'rare_count':int(rare.sum()),'dot_product':float(dot),'cosine':float(dot/(nc*nr).sqrt().clamp_min(1e-20)),'projected':bool(dot<0),'scope':'actual shared selected-transformer parameters; empirical current mini-batch'})
    else:(losses*w).sum().div(w.sum().clamp_min(1)).backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();targets+=len(target);weights+=float(w.sum())
    if step%64==0:save(arm['name']+' seed'+str(seed)+' step'+str(step))
    if step in [128,384,1152]:
     result=evaluate();path=D/(arm['name']+'_seed'+str(seed)+'_step'+str(step)+'.pt');torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'step':step,'arm':arm,'rng':rng.bit_generator.state,'seed':seed},path);m['rungs'].append({'arm':arm['name'],'seed':seed,'step':step,'processed_targets':targets,'sum_loss_weights':weights,'training_seconds':time.monotonic()-t,'development':result,'checkpoint_path':str(path),'checkpoint_sha256':sha(path)});save(arm['name']+' seed'+str(seed)+' rung'+str(step)+' complete');model.train()
 m.update(status='COMPLETE_TWO_SEED_CORE_MASK_AND_GRADIENT_PROJECTION_PILOT',finished=time.time(),native_archive_qualification=False,all96_exhausted=False);save('longer shared-core mask descendants complete; native and fresh corpus gates required')
except BaseException as e:
 v=globals().get('m',{});v.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());(M/'manifest.json').write_text(json.dumps(v,indent=2));print(v['traceback'],flush=True);raise
