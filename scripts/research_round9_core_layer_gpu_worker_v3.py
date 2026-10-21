"""Compare exact native FP32 input and13activation stages with GPU hooks."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='0';os.environ['OMP_NUM_THREADS']='2'
import pathlib,json,ast,time,traceback,hashlib
R=pathlib.Path('/kaggle/working/hp_round9');M=R/'core_layer_gpu_v3';M.mkdir(exist_ok=False)
src=(R/'research_round9_core_training_worker_v2.py').read_text().replace("D=R/'core_training_v2'","D=pathlib.Path('/root/hp_round9/core_layer_gpu_v3')")
src=src.replace("(D/'manifest.json').write_text(json.dumps(m,indent=2))","(D/'manifest.json').write_text(json.dumps(m,indent=2));(M/'manifest.json').write_text(json.dumps(m,indent=2))")
tree=ast.parse(src);chosen=[];found=False
for node in tree.body:
 if isinstance(node,ast.Try):
  for statement in node.body:
   if isinstance(statement,ast.Expr) and isinstance(statement.value,ast.Call) and isinstance(statement.value.func,ast.Name) and statement.value.func.id=='save' and statement.value.args and isinstance(statement.value.args[0],ast.Constant) and str(statement.value.args[0].value).startswith('actual selected core imported;'):
    found=True;break
   chosen.append(statement)
  break
 chosen.append(node)
assert found
try:
 exec(compile(ast.Module(body=chosen,type_ignores=[]),'<executed-core-import-only>','exec'),globals());m.update(scope='layer differential with full FP32 native priors; no SGD',rows=[],setup_sha256=hashlib.sha256((R/'research_round9_core_training_worker_v2.py').read_bytes()).hexdigest());save('aligning native actual step records with decoder article resets')
 ready=json.loads((R/'core_layer_probe_v1/manifest.json').read_text());assert ready['status']=='COMPLETE_NATIVE_CORE_LAYER_OBSERVATION';probe=pathlib.Path(ready['scratch'])/'layers.bin';dtype=np.dtype([('token','u1'),('prior','<f4',(205,)),('layers','<f4',(13,192)),('probs','<f4',(205,))]);records=np.fromfile(probe,dtype);active=np.ones(len(tokens),bool);active[bounds[1:]-1]=False;positions=np.where(active)[0][:len(records)];assert np.array_equal(tokens[positions],records['token']),'native step tokens differ from predicted boundary convention';m['native_step_token_position_alignment']='PASS';m['prior_f16_roundtrip_match']=bool(np.array_equal(records['prior'].astype('<f2'),np.asarray(prior[positions],'<f2')))
 # Scatter recorded full FP32 priors into their true input positions; terminal
 # fallback rows have no native step and are excluded from comparisons.
 dense_prior=np.asarray(prior[:int(positions[-1])+1],np.float32).copy();dense_prior[positions]=records['prior'];record_at={int(p):i for i,p in enumerate(positions)};capture={};hooks=[]
 def pre(module,args,kwargs):capture['initial']=args[0].detach().cpu().numpy()[0]
 hooks.append(model.blocks[0].register_forward_pre_hook(pre,with_kwargs=True))
 for layer,block in enumerate(model.blocks):
  def hook(module,args,out,idx=layer):capture[idx]=out.detach().cpu().numpy()[0]
  hooks.append(block.register_forward_hook(hook))
 from research_round9_native_integer_linear_v2 import install
 m['native_integer_linear_sites']=install(model)
 model.eval()
 with torch.no_grad():
  for a,b in zip(bounds[:-1],bounds[1:]):
   a=int(a);b=min(int(b),int(positions[-1])+1)
   if b<=a:break
   capture.clear();cu=torch.tensor([[0,b-a]],dtype=torch.int32,device='cuda');x=torch.tensor(tokens[a:b],device='cuda')[None];pr=torch.tensor(dense_prior[a:b],device='cuda')[None];q=model.compute_logits(x,pr,cu)[0].softmax(-1).cpu().numpy();valid=np.array([p for p in range(a,b) if p in record_at]);ix=np.array([record_at[int(p)] for p in valid]);local=valid-a
   if not len(valid):continue
   layers=np.stack([capture['initial'],*[capture[l] for l in range(12)]],1)[local];native=records['layers'][ix];stats=[]
   for l in range(13):
    diff=layers[:,l].astype(np.float64)-native[:,l].astype(np.float64);stats.append({'stage':l,'mean_abs':float(np.abs(diff).mean()),'max_abs':float(np.abs(diff).max()),'rms':float(np.sqrt(np.mean(diff*diff))),'first_token_max_abs':float(np.max(np.abs(diff[0])))})
   p=records['probs'][ix].astype(np.float64);qq=q[local].astype(np.float64);p=np.maximum(p,1e-6);p/=p.sum(-1,keepdims=True);qq=np.maximum(qq,1e-6);qq/=qq.sum(-1,keepdims=True);m['rows'].append({'article_start':a,'rows':len(valid),'stages':stats,'mean_native_GPU_KL_bits':float(np.sum(p*np.log2(p/qq),-1).mean()),'max_probability_difference':float(np.max(np.abs(p-qq)))});save('compared exact FP32 prior article at'+str(a))
 m.update(status='COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL',finished=time.time(),parity_repaired=False);save('layer mismatch localized; no native-export success inferred')
except BaseException as e:
 v=globals().get('m',{});v.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());(M/'manifest.json').write_text(json.dumps(v,indent=2));print(v['traceback'],flush=True);raise

