"""Localize failed packed/separate GPU invariance before claiming faster training.

Four finite inference backends with initial+12-block traces. A forward-only
recurrent repair is not certified as a differentiable training backend.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='0';os.environ['OMP_NUM_THREADS']='2'
import pathlib,json,time,traceback,ast,copy,math
R=pathlib.Path('/kaggle/working/hp_round9');M=R/'packing_differential_v1';M.mkdir(exist_ok=False)
status={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[]};(M/'manifest.json').write_text(json.dumps(status,indent=2))
try:
 text=(R/'research_round9_core_pipeline_profile_worker.py').read_text().replace("M=R/'core_pipeline_profile_v1'","M=R/'packing_differential_v1'").replace('/root/hp_round9/core_pipeline_profile_v1','/root/hp_round9/packing_differential_v1')
 tree=ast.parse(text);chosen=[]
 for node in tree.body:
  if isinstance(node,ast.Try):
   for stmt in node.body:
    if isinstance(stmt,ast.For) and isinstance(stmt.target,ast.Name) and stmt.target.id=='mode':break
    chosen.append(stmt)
   break
  # Own metadata directory already exists; imported setup must not recreate it.
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='R' for t in node.targets):continue
  if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='mkdir':continue
  chosen.append(node)
 exec(compile(ast.Module(body=chosen,type_ignores=[]),'<executed-profile-setup-only>','exec'),globals());m.update(scope='packed/separate fidelity localization with zero-update original core; no SGD',comparisons=[])
 original_rope=tfh.M.make_rope_args;positions=None
 def rope(*args,**kwargs):
  result=original_rope(*args,**kwargs)
  if positions is None:return result
  from dataclasses import replace
  return replace(result,sines=result.sines[positions],cosines=result.cosines[positions])
 tfh.M.make_rope_args=rope;captured={};hooks=[]
 def pre(module,args,kwargs):captured['initial']=args[0].detach().clone()[0]
 hooks.append(model.blocks[0].register_forward_pre_hook(pre,with_kwargs=True))
 for layer,block in enumerate(model.blocks):
  def hook(module,args,out,index=layer):captured[index]=out.detach().clone()[0]
  hooks.append(block.register_forward_hook(hook))
 def forward_trace(x,p,cu,pos):
  global positions
  positions=pos;captured.clear();q=model.compute_logits(x,p,cu)[0].softmax(-1);return q,torch.stack([captured['initial'],*[captured[k] for k in range(12)]],1)
 old_conv=tfh.M.causal_conv1d;old_kda=tfh.M.chunk_kda
 import research_round9_kda_reference as ref
 def conv(**kwargs):return ref.causal_conv1d_silu_reference(kwargs['x'],kwargs['weight'],kwargs.get('cu_seqlens'),dtype=torch.float32),None
 from fla.ops.kda.fused_recurrent import fused_recurrent_kda
 from research_round9_native_integer_linear_v2 import install
 model.eval();rec=data[('b','raw')]
 for backend in ['original','integer_linear','integer_reference_conv','integer_reference_conv_recurrent']:
  if backend=='integer_linear':m['integer_sites']=install(model)
  if backend=='integer_reference_conv':tfh.M.causal_conv1d=conv
  if backend=='integer_reference_conv_recurrent':tfh.M.chunk_kda=fused_recurrent_kda
  for cap in [256,1024]:
   docs=[(a,a+cap) for a,b in rec['articles'] if b-a>=cap][:4];assert len(docs)==4
   cuts=np.r_[0,np.cumsum([b-a for a,b in docs])].astype(np.int32);xs=[torch.tensor(rec['tokens'][a:b],device='cuda')[None] for a,b in docs];ps=[torch.tensor(np.asarray(rec['prior'][a:b],np.float32),device='cuda')[None] for a,b in docs];x=torch.cat(xs,1);p=torch.cat(ps,1);cu=torch.tensor(cuts[None],device='cuda');pos=torch.tensor(np.tile(np.arange(cap),4),device='cuda')
   with torch.no_grad():
    separated=[forward_trace(xx,pp,torch.tensor([[0,cap]],device='cuda',dtype=torch.int32),None) for xx,pp in zip(xs,ps)];sq=torch.cat([v[0] for v in separated]);sl=torch.cat([v[1] for v in separated]);pq,pl=forward_trace(x,p,cu,pos);changed=x.clone();changed[:,cap:]=0;fq,fl=forward_trace(changed,p,cu,pos)
   stages=[{'stage':k,'first_doc_max_abs':float((sl[:cap,k]-pl[:cap,k]).abs().max()),'later_docs_max_abs':float((sl[cap:,k]-pl[cap:,k]).abs().max())} for k in range(13)];err=float((sq-pq).abs().max());noninterference=float((pq[:cap]-fq[:cap]).abs().max());m['comparisons'].append({'backend':backend,'context_cap':cap,'documents':4,'probability_max_difference':err,'future_document_noninterference_probability_max_difference':noninterference,'stages':stages,'forward_tolerance_passed':err<=1e-5 and noninterference<=1e-6,'backward_certified':False});save(backend+' cap'+str(cap)+' packed stages compared')
 tfh.M.make_rope_args=original_rope;tfh.M.causal_conv1d=old_conv;tfh.M.chunk_kda=old_kda;m.update(status='COMPLETE_PACKED_GPU_BACKEND_LAYER_LOCALIZATION',finished=time.time());save('packed differential trace complete; backward/native qualification still required')
except BaseException as e:
 v=globals().get('m',status);v.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());(M/'manifest.json').write_text(json.dumps(v,indent=2));print(v['traceback'],flush=True);raise
