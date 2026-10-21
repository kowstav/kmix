"""Direct full-word supervision before native-relative mixture training.

An almost-closed mixture gate can starve a new dictionary head of gradients.
Train its normalized44515word law directly on verified dictionary events first,
then optimize full bit likelihood. Labels are supervision, never predictor input.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='1';os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import pathlib,json,time,traceback,ast
OUT=pathlib.Path('/kaggle/working/hp_round9');M=OUT/'word_warmstart_v1';M.mkdir(exist_ok=False)
status={'status':'WAITING_FOR_GPU1_WORD_SOFTMAX_V2','pid':os.getpid(),'started':time.time(),'stage':'queued until preceding worker completes; no duplicate GPU use','spending_usd':0,'deletions':[]};(M/'manifest.json').write_text(json.dumps(status,indent=2))
try:
 start=time.time()
 while True:
  prior=json.loads((OUT/'word_softmax_v2/manifest.json').read_text())
  if prior['status'].startswith('COMPLETE'):break
  if prior['status']=='FAIL':raise RuntimeError(prior['error'])
  assert time.time()-start<7200;time.sleep(10)
 source=OUT/'research_round9_word_softmax_v2_worker.py';text=source.read_text().replace("D=OUT/'word_softmax_v2'","D=OUT/'word_warmstart_v1_setup'").replace("S=pathlib.Path('/root/hp_round9/word_softmax_v2')","S=pathlib.Path('/root/hp_round9/word_warmstart_v1')").replace("(D/'manifest.json').write_text(json.dumps(m,indent=2))","(D/'manifest.json').write_text(json.dumps(m,indent=2));(M/'manifest.json').write_text(json.dumps(m,indent=2))")
 tree=ast.parse(text);selected=[];found=False
 for node in tree.body:
  if isinstance(node,ast.Try):
   for stmt in node.body:
    if isinstance(stmt,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='data' for t in stmt.targets):found=True;break
    selected.append(stmt)
   break
  selected.append(node)
 assert found;exec(compile(ast.Module(body=selected,type_ignores=[]),'<normalized-model-setup-only>','exec'),globals())
 m.update(scope='direct word-class warm start then full-bit mixture training, spelling/independent/random controls; no original-core retraining',word_rungs=[],rungs=[],confirmation=[],parent_source_sha256=sha(source),worker_sha256=sha(OUT/'research_round9_word_warmstart_worker.py'),scratch=str(S))
 data={s:load(s) for s in 'abcd'};train={k:np.concatenate([data[s][k] for s in 'ab']) for k in data['a']};dev={k:np.concatenate([data[s][k] for s in 'cd']) for k in data['c']};tb={k:torch.as_tensor(v,device='cuda') for k,v in train.items()};lookup={w:j for j,w in enumerate(words)};worddata={s:{'history':[],'target':[]} for s in 'abcdef'}
 wm=json.loads((OUT/'word_events_v1/manifest.json').read_text());assert wm['status'].startswith('COMPLETE');ev=pathlib.Path(wm['scratch'])/'events.tsv';assert sha(ev)==wm['event_file_sha256']
 for line in ev.open():
  ix,lo,hi,complete,body,w=line.rstrip().split('\t');s='abcdef'[int(ix)]
  if s not in 'abcd' or w not in lookup:continue
  rec=data[s];start=wm['windows'][int(ix)]['start'];lo=int(lo)-start;hi=int(hi)-start;segment=rec['raw'][lo:hi];skip=0
  while skip<len(segment) and skip<3 and inv(int(segment[skip])) in [6,7,64]:skip+=1
  encoded_word=np.array([inv(v) for v in encode(lookup[w])]);pos=lo+skip
  if not np.array_equal(segment[skip:],encoded_word) or pos<16 or not rec['active'][pos] or rec['node'][pos]!=0:continue
  worddata[s]['history'].append(rec['history'][pos]);worddata[s]['target'].append(lookup[w])
 for s in 'abcd':
  worddata[s]={k:np.asarray(v,dtype=np.float32 if k=='history' else np.int64) for k,v in worddata[s].items()};assert len(worddata[s]['target'])>100
 wt={k:torch.tensor(np.concatenate([worddata[s][k] for s in 'ab']),device='cuda') for k in ['history','target']};wd={k:np.concatenate([worddata[s][k] for s in 'cd']) for k in ['history','target']}
 def word_logits(model,h):
  query=model.context(h)
  if model.kind=='spelling':e=model.composer(torch.cat([bags,model.letter(letters).flatten(1)],-1))
  elif model.kind=='word_embedding':e=model.word.weight
  else:e=model.random
  return model.log_scale.exp().clamp(.01,8)*(query@e.T)-model.zipf_exponent.clamp(0,3)*model.rank[None]
 def word_score(model):
  loss=0.;model.eval()
  with torch.no_grad():
   for lo in range(0,len(wd['target']),256):
    h=torch.as_tensor(wd['history'][lo:lo+256],device='cuda');target=torch.as_tensor(wd['target'][lo:lo+256],device='cuda');loss+=float(F.cross_entropy(word_logits(model,h),target,reduction='sum'))
  return {'bits_per_dictionary_word':loss/math.log(2)/len(wd['target']),'words':len(wd['target'])}
 m['contract']={'arms':['spelling','word_embedding','random_basis'],'seeds':[7106,7107],'word_pretrain_rungs':[128,384],'joint_bit_rungs':[128,384],'word_batch':256,'joint_batch_bytes':128,'word_supervision':'full decoded dictionary word whose complete encoded span equals its verified native code plus optional leading case controls; hidden before first code byte; root known-prefix only','labels':'word class and frequency are never model inputs; body flag not used','objective':'direct normalized44515class cross entropy then ordinary full-bit native-adaptive mixture cross entropy','selection':'all six matched arms warm+joint; choose best full-bit C/D finalist per seed before E/F; word CE improvement alone does not qualify','scope':'fit-held-out fragments only; native model/executable/fullwarm/resources remain pending','word_event_counts':{s:len(worddata[s]['target']) for s in 'abcd'}};save('exact first-code word targets ready; gradient-starvation descendant begins')
 models={}
 for seed in [7106,7107]:
  for kind in ['spelling','word_embedding','random_basis']:
   key=kind+'_seed'+str(seed);torch.manual_seed(seed);model=Model(kind).cuda();models[key]=model;opt=torch.optim.AdamW(model.parameters(),lr=.003,weight_decay=0);gen=torch.Generator(device='cuda').manual_seed(seed);model.train();start=time.monotonic()
   for step in range(1,385):
    ix=torch.randint(len(wt['target']),(256,),device='cuda',generator=gen);opt.zero_grad(set_to_none=True);F.cross_entropy(word_logits(model,wt['history'][ix]),wt['target'][ix]).backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step()
    if step%64==0:save(key+' word pretrain'+str(step))
    if step in [128,384]:
     result=word_score(model);path=S/(key+'_word_step'+str(step)+'.pt');torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'phase':'word','step':step,'key':key},path);m['word_rungs'].append({'key':key,'step':step,'development':result,'seconds':time.monotonic()-start,'checkpoint_path':str(path),'checkpoint_sha256':sha(path)});save(key+' word rung complete');model.train()
   # Deliberately fresh optimizer for the joint full-bit objective.
   opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=0);gen=torch.Generator(device='cuda').manual_seed(seed);start=time.monotonic();model.train()
   for step in range(1,385):
    ix=torch.randint(len(train['y']),(128,),device='cuda',generator=gen);b={k:v[ix] for k,v in tb.items() if k!='y'};opt.zero_grad(set_to_none=True);F.binary_cross_entropy(model(**b),tb['y'][ix]).backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step()
    if step%64==0:save(key+' full-bit'+str(step))
    if step in [128,384]:
     result=score(model,dev);path=S/(key+'_joint_step'+str(step)+'.pt');torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'phase':'joint','step':step,'key':key},path);weightbytes=b''.join(v.detach().cpu().numpy().tobytes() for v in model.state_dict().values());m['rungs'].append({'key':key,'step':step,'development':result,'seconds':time.monotonic()-start,'zlib9_state_bytes':len(zlib.compress(weightbytes,9)),'checkpoint_path':str(path),'checkpoint_sha256':sha(path)});save(key+' full-bit rung complete');model.train()
 finalists=[]
 for seed in [7106,7107]:
  rows=[v for v in m['rungs'] if v['step']==384 and v['key'].endswith('seed'+str(seed))];rows.sort(key=lambda v:v['development']['gain_vs_adaptive_bytes'],reverse=True);finalists.append(rows[0]['key'])
 m['frozen_finalists_before_EF']=finalists;save('warm-start finalists selected on actual full-bit development')
 for s in 'ef':
  rec=load(s)
  for key in finalists:m['confirmation'].append({'slice':s,'key':key,'result':score(models[key],rec)});save(key+' '+s+' confirmation')
 m.update(status='COMPLETE_DIRECT_WORD_WARMSTART_THEN_FULL_BIT_MIXTURE_SCREEN',finished=time.time(),native_or_full_package_qualified=False);save('direct word-supervision descendant complete')
except BaseException as e:
 v=globals().get('m',status);v.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());(M/'manifest.json').write_text(json.dumps(v,indent=2));print(v['traceback'],flush=True);raise
