"""Stronger normalized word composer: learned literal branch and mixture gate.

V1 had a fixed uniform literal branch, a fixed dot-product scale and a .1 gate
cap. This controlled descendant learns those quantities and compares a byte
head of matched context. No target word/frequency or unpriced future input.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='1';os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import pathlib,json,time,hashlib,traceback,re,math,zlib,ast
import numpy as np,torch
from torch import nn
from torch.nn import functional as F
from numba import njit
from scipy.special import expit
R=pathlib.Path('/kaggle/working/hp_round8');OUT=pathlib.Path('/kaggle/working/hp_round9');D=OUT/'word_softmax_v2';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/word_softmax_v2');S.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[],'scope':'learned literal distribution, dictionary/literal gate, .5 mixture cap and learned word scale with byte-head control','rungs':[],'confirmation':[],'scratch':str(S)}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 old=ast.parse((OUT/'research_round9_word_softmax_worker.py').read_text());fs=[n for n in old.body if isinstance(n,ast.FunctionDef) and n.name in ['inv','encode','prepare_tree','parse_nodes','load','score']];exec(compile(ast.Module(body=fs,type_ignores=[]),'<unchanged-tree-loader-score>','exec'),globals())
 rt=ast.parse((OUT/'research_round9_adaptive_source_worker.py').read_text());ns={'np':np,'math':math,'njit':njit};exec(compile(ast.Module(body=[n for n in rt.body if isinstance(n,ast.FunctionDef) and n.name=='replay'],type_ignores=[]),'<adaptive>', 'exec'),ns);replay=ns['replay']
 torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;m['gpu']=torch.cuda.get_device_name(0);m['worker_sha256']=sha(OUT/'research_round9_word_softmax_v2_worker.py')
 words,nodes,cc,aa,dd,bg,ll=prepare_tree(R/'native_stage_trace_v1/tree/dictionary/english.dic');codes=torch.tensor(cc,device='cuda');allowed=torch.tensor(aa,device='cuda');depths=torch.tensor(dd,device='cuda');bags=torch.tensor(bg,device='cuda');letters=torch.tensor(ll,device='cuda');alphabet=torch.arange(256,device='cuda');alphabet_bit=torch.stack([(alphabet>>(7-b))&1 for b in range(8)])
 class Model(nn.Module):
  def __init__(self,kind):
   super().__init__();self.kind=kind;self.context=nn.Sequential(nn.Linear(192,32),nn.Tanh());self.alpha=nn.Linear(32,1);nn.init.zeros_(self.alpha.weight);nn.init.constant_(self.alpha.bias,-5.);self.literal=nn.Linear(32,256);self.word_gate=nn.Linear(32,1);nn.init.zeros_(self.word_gate.weight);nn.init.constant_(self.word_gate.bias,1.4)
   if kind=='spelling':self.letter=nn.Embedding(27,4);self.composer=nn.Sequential(nn.Linear(58,64),nn.GELU(),nn.Linear(64,32))
   elif kind=='word_embedding':self.word=nn.Embedding(44515,32)
   elif kind=='random_basis':self.register_buffer('random',torch.tensor(np.random.default_rng(6906).standard_normal((44515,32)).astype(np.float32)/math.sqrt(32)))
   self.zipf_exponent=nn.Parameter(torch.tensor(1.));self.log_scale=nn.Parameter(torch.tensor(math.log(.2)));self.register_buffer('rank',torch.log(torch.arange(1,44516,dtype=torch.float32)))
  def forward(self,history,node,active,raw,p,native_p=None,neutral=False):
   h=self.context(history);literal=self.literal(h).softmax(-1)
   if self.kind=='byte_control':bytep=literal
   else:
    if self.kind=='spelling':e=self.composer(torch.cat([bags,self.letter(letters).flatten(1)],-1))
    elif self.kind=='word_embedding':e=self.word.weight
    elif self.kind=='random_basis':e=self.random
    else:e=torch.zeros((44515,32),device='cuda')
    logits=self.log_scale.exp().clamp(.01,8)*(h@e.T)-self.zipf_exponent.clamp(0,3)*self.rank[None];wp=logits.masked_fill(~allowed[node],-torch.inf).softmax(-1);values=codes[:,depths[node]].T;wordp=torch.zeros(len(node),256,device='cuda');wordp.scatter_add_(1,values,wp);gate=torch.sigmoid(self.word_gate(h));bytep=gate*wordp+(1-gate)*literal
   al=.5*torch.sigmoid(self.alpha(h))*active[:,None]
   if neutral:al=al*0
   rows=[]
   for bit in range(8):
    mask=0xff^(0xff>>bit);prefix=raw&mask;keep=(alphabet[None]&mask)==prefix[:,None];mass=bytep*keep;expert=(mass*alphabet_bit[bit][None]).sum(-1)/mass.sum(-1).clamp_min(1e-20);rows.append((1-al[:,0])*p[:,bit]+al[:,0]*expert)
   return torch.stack(rows,1).clamp(1/65536,65535/65536)
 data={s:load(s) for s in 'abcd'};train={k:np.concatenate([data[s][k] for s in 'ab']) for k in data['a']};dev={k:np.concatenate([data[s][k] for s in 'cd']) for k in data['c']};tb={k:torch.as_tensor(v,device='cuda') for k,v in train.items()};models={};opts={};steps={}
 m['contract']={'arms':['byte_control','static_rank','spelling','word_embedding','random_basis'],'seeds':[6906,6907],'rungs':[128,384,1152],'selection':'CD only; best2/seed after128, best1/seed after384; EF fit-held-out confirmation','batch_bytes':128,'objective':'ordinary full bit loss; frozen causal adaptive native Q16 reference','literal':'learned normalized256byte softmax, positive support','word':'exact44515normalized code-tree word distribution; learned bounded temperature and Zipf exponent','gate':'learned dictionary/literal gate and .5cap native/expert gate, before-target hidden only','unimplemented':'native CPU integration, production framing, fullwarm/package, exhaustive architectures'}
 for seed in [6906,6907]:
  for kind in m['contract']['arms']:
   key=kind+'_seed'+str(seed);torch.manual_seed(seed);model=Model(kind).cuda();models[key]=model;opts[key]=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=0);steps[key]=0;b={k:v[:16].clone() for k,v in tb.items() if k!='y'}
   with torch.no_grad():
    assert torch.equal(model(**b,neutral=True),b['p']);q=model(**b);b['history'][8:]=2;b['raw'][8:]=0;b['node'][8:]=0;assert torch.equal(q[:8],model(**b)[:8])
 m['nonzero_future_prefix_and_zero_identity']='PASS';survivors=list(models);save('ten stronger word and matched byte-head runs starting')
 for rung in [128,384,1152]:
  for key in survivors:
   model=models[key];model.train();opt=opts[key];gen=torch.Generator(device='cuda').manual_seed(int(key.split('seed')[-1])+steps[key]*101);start=time.monotonic()
   while steps[key]<rung:
    ix=torch.randint(len(train['y']),(128,),device='cuda',generator=gen);b={k:v[ix] for k,v in tb.items() if k!='y'};opt.zero_grad(set_to_none=True);q=model(**b);F.binary_cross_entropy(q,tb['y'][ix]).backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();steps[key]+=1
    if steps[key]%64==0:save(key+' step'+str(steps[key]))
   result=score(model,dev);path=S/(key+'_step'+str(rung)+'.pt');torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'steps':rung,'key':key},path);weights=b''.join(v.detach().cpu().numpy().tobytes() for v in model.state_dict().values());m['rungs'].append({'key':key,'step':rung,'development':result,'training_seconds_this_rung':time.monotonic()-start,'parameters':sum(p.numel() for p in model.parameters()),'zlib9_state_bytes':len(zlib.compress(weights,9)),'checkpoint_path':str(path),'checkpoint_sha256':sha(path)});save(key+' rung complete')
  if rung<1152:
   survivors=[]
   for seed in [6906,6907]:
    rows=[r for r in m['rungs'] if r['step']==rung and r['key'].endswith('seed'+str(seed))];rows.sort(key=lambda r:r['development']['gain_vs_adaptive_bytes'],reverse=True);survivors.extend(r['key'] for r in rows[:2 if rung==128 else 1])
   m.setdefault('selections',[]).append({'rung':rung,'survivors':survivors})
 m['frozen_finalists']=survivors;save('stronger word-head finalists frozen')
 for s in 'ef':
  rec=load(s)
  for key in survivors:m['confirmation'].append({'slice':s,'key':key,'result':score(models[key],rec)});save(key+' '+s+' confirmation')
 m.update(status='COMPLETE_LEARNED_LITERAL_WORD_COMPOSER_DESCENDANT_SCREEN',finished=time.time(),native_or_full_package_qualified=False);save('stronger finite descendant complete')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
