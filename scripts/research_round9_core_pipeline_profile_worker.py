"""Queued original-core zero E/F control and honest packed-pipeline benchmark.

Do not interrupt live training. No optimizer changes to model weights (lr0).
Packed batching must reset KDA/convolutions/attention and RoPE per document.
Timing is GPU/T4 evidence, not a 5090 throughput claim or archive qualification.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='0';os.environ['OMP_NUM_THREADS']='2'
import pathlib,json,time,traceback,ast,math,copy
R=pathlib.Path('/kaggle/working/hp_round9');M=R/'core_pipeline_profile_v1';M.mkdir(exist_ok=False)
status={'status':'WAITING_FOR_CORE_DISTRIBUTED_V2','pid':os.getpid(),'started':time.time(),'stage':'wait for preceding GPU0 job; do not duplicate or interfere','spending_usd':0,'deletions':[]};(M/'manifest.json').write_text(json.dumps(status,indent=2))
try:
 start=time.time()
 while True:
  previous=json.loads((R/'core_distributed_v2/manifest.json').read_text())
  if previous['status'].startswith('COMPLETE'):break
  if previous['status']=='FAIL':raise RuntimeError(previous['error'])
  assert time.time()-start<10800;time.sleep(10)
 source=R/'research_round9_core_training_worker_v2.py';text=source.read_text().replace("D=R/'core_training_v2'","D=pathlib.Path('/root/hp_round9/core_pipeline_profile_v1')").replace("(D/'manifest.json').write_text(json.dumps(m,indent=2))","(D/'manifest.json').write_text(json.dumps(m,indent=2));(M/'manifest.json').write_text(json.dumps(m,indent=2))")
 tree=ast.parse(text);selected=[];found=False
 for node in tree.body:
  if isinstance(node,ast.Try):
   for stmt in node.body:
    if isinstance(stmt,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='tokens' for t in stmt.targets):found=True;break
    selected.append(stmt)
   break
  selected.append(node)
 assert found;exec(compile(ast.Module(body=selected,type_ignores=[]),'<selected-core-setup-only>', 'exec'),globals());m.update(scope='unchanged selected-core E/F zero control and packed GPU pipeline profiling,lr0',worker_sha256=sha(R/'research_round9_core_pipeline_profile_worker.py'),timings=[],packing_checks=[],baseline_EF={})
 ready_data=json.loads((R/'distributed_core_data_v1/manifest.json').read_text());assert ready_data['status'].startswith('COMPLETE');data={}
 for row in ready_data['slices']:
  root=pathlib.Path(row['files'][0]['path']).parent;tok=np.fromfile(root/'tokens.u8','u1').astype(np.int64);fr=np.fromfile(root/'word_frequency.i32','<i4');pr=np.memmap(root/'priors.f16','<f2','r',shape=(len(tok),205));bd=np.fromfile(root/'bounds.i32','<i4');articles=[(int(a),int(b)) for a,b in zip(bd[:-1],bd[1:]) if b-a>=65];data[(row['slice'],row['mode'])]={'tokens':tok,'freq':fr,'prior':pr,'articles':articles}
 def single(rec,a,b):
  x=torch.as_tensor(rec['tokens'][a:b],device='cuda')[None];p=torch.as_tensor(np.asarray(rec['prior'][a:b],np.float32),device='cuda')[None];cu=torch.tensor([[0,b-a]],dtype=torch.int32,device='cuda');return model.compute_logits(x,p,cu)[0].float()
 model.eval()
 for mode in ['raw','redacted1392']:
  total=common=rare=0.;nt=nc=nr=0
  with torch.no_grad():
   for s in 'ef':
    rec=data[(s,mode)]
    for a,b in rec['articles']:
     b=min(b,a+1024);z=single(rec,a,b)[:-1];target=torch.tensor(rec['tokens'][a+1:b],device='cuda');l=F.cross_entropy(z,target,reduction='none').cpu().numpy()/math.log(2);fr=rec['freq'][a+1:b];rm=(fr>=0)&(fr<1392);total+=float(l.sum());common+=float(l[~rm].sum());rare+=float(l[rm].sum());nt+=len(l);nc+=int((~rm).sum());nr+=int(rm.sum())
  m['baseline_EF'][mode]={'all_bits_per_symbol':total/nt,'common_or_unlabelled_bits_per_symbol':common/nc,'rare_or_redacted_bits_per_symbol':rare/max(1,nr),'targets':nt,'common_targets':nc,'rare_targets':nr,'mode':mode,'slices':'ef'};save('unchanged selected-core '+mode+' E/F baseline')
 original_rope=tfh.M.make_rope_args;rope_positions=None
 def per_document_rope(*args,**kwargs):
  r=original_rope(*args,**kwargs)
  if r is None or rope_positions is None:return r
  from dataclasses import replace
  return replace(r,sines=r.sines[rope_positions],cosines=r.cosines[rope_positions])
 tfh.M.make_rope_args=per_document_rope
 rec=data[('b','raw')];initial=copy.deepcopy(model.state_dict())
 for cap in [256,1024]:
  docs=[]
  for a,b in rec['articles']:
   if b-a>=cap:docs.append((a,a+cap))
   if len(docs)==8:break
  if len(docs)<2:continue
  for count in [1,4,8]:
   chosen=docs[:count];cuts=np.r_[0,np.cumsum([b-a for a,b in chosen])].astype(np.int32);xt=torch.tensor(np.concatenate([rec['tokens'][a:b] for a,b in chosen]),device='cuda')[None];pt=torch.tensor(np.concatenate([np.asarray(rec['prior'][a:b],np.float32) for a,b in chosen]),device='cuda')[None];cu=torch.tensor(cuts[None],dtype=torch.int32,device='cuda');pos=torch.tensor(np.concatenate([np.arange(b-a) for a,b in chosen]),device='cuda');index=torch.tensor(np.concatenate([np.arange(cuts[k],cuts[k+1]-1) for k in range(len(chosen))]),device='cuda');target=xt[0,index+1]
   model.eval();rope_positions=None
   with torch.no_grad():separate=torch.cat([single(rec,a,b) for a,b in chosen]);rope_positions=pos;packed=model.compute_logits(xt,pt,cu)[0].float();err=float((separate.softmax(-1)-packed.softmax(-1)).abs().max());future_error=0.
   if count>1:
    with torch.no_grad():
     changed=xt.clone();changed[:,cuts[1]:]=0;q=model.compute_logits(changed,pt,cu)[0].float();future_error=float((q[:cuts[1]]-packed[:cuts[1]]).abs().max())
   accepted=err<=1e-5 and future_error<=1e-6;m['packing_checks'].append({'context_cap':cap,'documents':count,'probability_max_difference_from_separate':err,'first_document_future_noninterference_max_logit_difference':future_error,'tolerance_gate_passed':accepted,'native_probability_parity':'unresolved; this is GPU batching fidelity only'});save('packed document isolation measured')
   if not accepted:continue
   for foreach in [False,True]:
    model.load_state_dict(initial);model.train();opt=torch.optim.AdamW(model.parameters(),lr=0.,weight_decay=0,foreach=foreach);times=[];rope_positions=pos
    for step in range(30):
     torch.cuda.synchronize();start=time.perf_counter();opt.zero_grad(set_to_none=True);z=model.compute_logits(xt,pt,cu)[0].float();loss=F.cross_entropy(z[index],target);loss.backward();opt.step();torch.cuda.synchronize();elapsed=time.perf_counter()-start
     if step>=10:times.append(elapsed)
    assert all(torch.equal(v,model.state_dict()[k]) for k,v in initial.items()),'lr0 timing altered selected model'
    m['timings'].append({'context_cap':cap,'documents':count,'foreach_optimizer':foreach,'resident_forward_tokens':int(xt.numel()),'useful_next_token_targets':int(index.numel()),'warm_steps':10,'timed_steps':20,'median_step_seconds':float(np.median(times)),'p90_step_seconds':float(np.percentile(times,90)),'useful_targets_per_second':float(index.numel()/np.median(times)),'scope':'resident batch,FP32 selected QAT shadow,backward+Adamlr0; excludes data load/CPU native export/evaluation','peak_cuda_bytes':torch.cuda.max_memory_allocated()});save('packed original-core throughput measured')
 tfh.M.make_rope_args=original_rope;m.update(status='COMPLETE_SELECTED_CORE_ZERO_EF_AND_PACKED_PIPELINE_PROFILE',finished=time.time(),native_or_full_package_qualified=False);save('zero controls and real training-pipeline profile complete')
except BaseException as e:
 v=globals().get('m',status);v.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());(M/'manifest.json').write_text(json.dumps(v,indent=2));print(v['traceback'],flush=True);raise
