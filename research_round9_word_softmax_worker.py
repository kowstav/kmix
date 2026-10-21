"""Actual normalized word-code tree heads, not a byte-feature proxy.

An exact44515-way softmax is marginalized through the unchanged native WRT
code tree into next-byte probabilities. A uniform literal branch supplies full
support. Both the code node and each within-byte prefix are decoder-known.
Compare spelling sharing, independent word embeddings and a random basis.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='1';os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import pathlib,json,time,hashlib,traceback,re,math,zlib,ast
import numpy as np,torch
from torch import nn
from torch.nn import functional as F
R=pathlib.Path('/kaggle/working/hp_round8');OUT=pathlib.Path('/kaggle/working/hp_round9');D=OUT/'word_softmax_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/word_softmax_v1');S.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[],'scope':'exact dictionary word softmax and spelling composer on native decoder hidden states','rungs':[],'confirmation':[],'scratch':str(S)}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inv(c):
 if 123<=c<127:c-=43
 elif 80<=c<84:c+=43
 elif 58<=c<=63 or 74<=c<=79:c^=112
 if c in [88,96]:c^=56
 return c
def encode(j):
 if j<80:return [128+j]
 if j<3920:j-=80;return [208+j//80,128+j%80]
 j-=3920;return [240+(j//80)//32,208+(j//80)%32,128+j%80]
def prepare_tree(dictionary):
 words=re.findall('[a-z]+',dictionary.read_text());assert len(words)==44515
 nodes={():0};codes=np.zeros((len(words),3),np.int64);prefixes=[]
 for j,w in enumerate(words):
  seq=encode(j);codes[j,:len(seq)]=[inv(v) for v in seq]
  for n in range(1,len(seq)):
   pref=tuple(seq[:n])
   if pref not in nodes:nodes[pref]=len(nodes)
 allowed=np.zeros((len(nodes),len(words)),bool);depth=np.zeros(len(nodes),np.int64)
 for prefix,ix in nodes.items():
  depth[ix]=len(prefix)
  for j in range(len(words)):
   seq=encode(j)
   if tuple(seq[:len(prefix)])==prefix and len(seq)>len(prefix):allowed[ix,j]=True
  assert allowed[ix].any()
 # Every dictionary code leaf and every proper prefix has exactly its native path.
 for j in range(len(words)):
  seq=encode(j)
  for n in range(len(seq)):assert allowed[nodes[tuple(seq[:n])],j]
 bag=np.zeros((len(words),26),np.float32);letters=np.zeros((len(words),8),np.int64)
 for j,w in enumerate(words):
  for c in w:bag[j,ord(c)-97]+=1
  bag[j]/=max(1,len(w))
  for k,c in enumerate(w[:4]):letters[j,k]=ord(c)-96
  for k,c in enumerate(w[-4:]):letters[j,4+k]=ord(c)-96
 return words,nodes,codes,allowed,depth,bag,letters
def parse_nodes(raw,s,nodes):
 node=np.zeros(len(raw),np.int64);active=np.ones(len(raw),np.float32);prefix=();escape=False
 for i,b in enumerate(raw):
  if i<(6 if s=='a' else 0):active[i]=0;continue
  node[i]=nodes.get(prefix,0)
  if escape:active[i]=0;escape=False;prefix=();continue
  c=inv(int(b))
  if prefix:
   pref=prefix+(c,)
   prefix=pref if pref in nodes else ()
  elif c==12:escape=True
  elif c>=208:prefix=(c,) if (c,) in nodes else ()
  if i<16:active[i]=0
 return node,active
def load(s):
 base=R/'atom_cache_v1';root=(R/'native_stage_trace_v1' if s in 'ab' else R/'native_stage_weak_confirmation_v1' if s in 'cd' else R/'source_wide_confirmation_v1')/(s+'512k');rawpath=base/(s+'512k.bin') if s in 'abcd' else root/'input.bin';raw=np.frombuffer(rawpath.read_bytes(),'u1').copy();pp=base/(s+'_native/final_p.u16') if s in 'abcd' else root/'final_p.u16';hp=base/(s+'_native/hidden.q8') if s in 'abcd' else root/'hidden.q8'
 native_int=np.fromfile(pp,'<u2');native_p=native_int.reshape(-1,8).astype(np.float32)/65536;h=np.memmap(hp,'u1','r',shape=(len(raw),193));valid=np.r_[0,h[:-1,0]].astype(np.float32);history=np.vstack([np.zeros((1,192)),np.asarray(h[:-1,1:],np.float32)/127.5-1]);history*=valid[:,None];node,active=parse_nodes(raw,s,nodes);active*=valid;bits=((raw[:,None]>>(7-np.arange(8)))&1).astype(np.float32)
 ell=np.log(native_int.astype(np.float64)/(65536-native_int.astype(np.float64)));st=np.memmap(root/'stage.f32','<f4','r',offset=12,shape=(len(native_int),19));nn=np.clip(st[:,17].astype(np.float64),1/65536,65535/65536);feat=((np.clip(np.log(nn/(1-nn))-ell,-12,12)/12).astype(np.float32)*np.repeat(valid,8)).astype(np.float64);theta=np.array([.0016181118716570748,-.007454085408717222,2.3818512619982752],dtype=np.float64);dot=theta[0]+theta[1]*ell+theta[2]*feat;experts=np.column_stack([native_int,*[np.clip(np.floor(65536*expit(ell+scale*dot)+.5),1,65535).astype('<u2') for scale in [.5,1.,1.5,2.]]]);q=replay(experts,bits.reshape(-1).astype('u1'),2.6441431586476938e-06)[0];p=q.reshape(-1,8).astype(np.float32)/65536
 m.setdefault('inputs',[]).append({'slice':s,'raw_sha256':sha(rawpath),'native_p_sha256':sha(pp),'hidden_sha256':sha(hp),'adaptive_Q16_sha256':hashlib.sha256(q.tobytes()).hexdigest()});return {'history':history.astype(np.float32),'node':node,'active':active,'raw':raw.astype(np.int64),'p':p,'native_p':native_p,'y':bits}
class Model(nn.Module):
 def __init__(self,kind):
  super().__init__();self.kind=kind;self.query=nn.Sequential(nn.Linear(192,32),nn.Tanh());self.alpha=nn.Linear(192,1);nn.init.zeros_(self.alpha.weight);nn.init.constant_(self.alpha.bias,-5.)
  self.letter=nn.Embedding(27,4);self.composer=nn.Sequential(nn.Linear(26+32,64),nn.GELU(),nn.Linear(64,32));self.word=nn.Embedding(44515,32);self.zipf_exponent=nn.Parameter(torch.tensor(1.));self.register_buffer('rank',torch.log(torch.arange(1,44516,dtype=torch.float32)));self.register_buffer('random',torch.tensor(np.random.default_rng(6806).standard_normal((44515,32)).astype(np.float32)/math.sqrt(32)))
 def forward(self,history,node,active,raw,p,native_p=None,neutral=False):
  if self.kind=='spelling':e=self.composer(torch.cat([bags,self.letter(letters).flatten(1)],-1))
  elif self.kind=='word_embedding':e=self.word.weight
  elif self.kind=='random_basis':e=self.random
  else:e=self.random*0
  q=self.query(history);logits=.2*q@e.T-self.zipf_exponent.clamp(0,2)*self.rank[None];valid=allowed[node];logits=logits.masked_fill(~valid,-torch.inf);wp=logits.softmax(-1);depth=depths[node];values=codes[:,depth].T;bytep=torch.zeros(len(node),256,device='cuda');bytep.scatter_add_(1,values,wp);bytep=.8*bytep+.2/256
  al=.1*torch.sigmoid(self.alpha(history))*active[:,None]
  if neutral:al=al*0
  rows=[]
  for bit in range(8):
   keepmask=0xff^(0xff>>(bit));prefix=raw&keepmask;keep=(alphabet[None]&keepmask)==prefix[:,None];num=(bytep*keep*(alphabet_bit[bit][None])).sum(-1);den=(bytep*keep).sum(-1);expert=num/den.clamp_min(1e-20);rows.append((1-al[:,0])*p[:,bit]+al[:,0]*expert)
  return torch.stack(rows,1).clamp(1/65536,65535/65536)
def score(model,rec):
 model.eval();gain=nativegain=0.;qh=hashlib.sha256();start=time.monotonic()
 with torch.no_grad():
  for lo in range(0,len(rec['y']),128):
   hi=min(lo+128,len(rec['y']));b={k:torch.as_tensor(v[lo:hi],device='cuda') for k,v in rec.items() if k!='y'};prob=model(**b).cpu().numpy().astype(np.float64);q=np.clip(np.floor(prob*65536+.5),1,65535).astype('<u2');p=rec['p'][lo:hi].astype(np.float64)*65536;y=rec['y'][lo:hi].astype(bool);sel=np.where(y,q.astype(np.float64),65536-q.astype(np.float64));gain+=float(np.log2(sel/np.where(y,p,65536-p)).sum()/8);np0=rec['native_p'][lo:hi].astype(np.float64)*65536;nativegain+=float(np.log2(sel/np.where(y,np0,65536-np0)).sum()/8);qh.update(q.tobytes())
 return {'gain_vs_adaptive_bytes':gain,'gain_vs_native_bytes':nativegain,'Q16_sha256':qh.hexdigest(),'wall_seconds':time.monotonic()-start}
try:
 from numba import njit
 from scipy.special import expit
 replay_tree=ast.parse((OUT/'research_round9_adaptive_source_worker.py').read_text());replay_nodes=[n for n in replay_tree.body if isinstance(n,ast.FunctionDef) and n.name=='replay'];namespace={'np':np,'math':math,'njit':njit};exec(compile(ast.Module(body=replay_nodes,type_ignores=[]),'<frozen-adaptive-replay>','exec'),namespace);replay=namespace['replay']
 torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;m['gpu']=torch.cuda.get_device_name(0);m['worker_sha256']=sha(OUT/'research_round9_word_softmax_worker.py');dictionary=R/'native_stage_trace_v1/tree/dictionary/english.dic';words,nodes,cc,aa,dd,bg,ll=prepare_tree(dictionary);codes=torch.tensor(cc,device='cuda');allowed=torch.tensor(aa,device='cuda');depths=torch.tensor(dd,device='cuda');bags=torch.tensor(bg,device='cuda');letters=torch.tensor(ll,device='cuda');alphabet=torch.arange(256,device='cuda');alphabet_bit=torch.stack([(alphabet>>(7-b))&1 for b in range(8)])
 m['tree']={'dictionary_sha256':sha(dictionary),'leaves':len(words),'proper_prefix_nodes':len(nodes),'all_codes_and_proper_prefixes_validated':True};m['contract']={'arms':['static_rank','spelling','word_embedding','random_basis'],'seeds':[6806,6807],'rungs':[128,384,1152],'batch_completed_byte_contexts':128,'full_bit_targets_per_step':1024,'objective':'ordinary full-bit adaptive-relative mixture loss; no rare masks','softmax':'exact44515-way dictionary code distribution; known-prefix normalization; .2uniform literal branch across256bytes','mixture':'nonnegative context gate capped.1 with frozen causal scaled5H262144 adaptive integer law, gated previous valid hidden; no target/oracle routing','word_input':'already-decoded native hidden192; no word-event frequency labels','parser':'unchanged WRT code tree; known semantic body, cold initial16bytes and escapes suppressed; full production framing parser still required','literal_support':'positive uniform branch; native mixture supplies full support','parameter_cost':'all shipped learned arrays must be priced; unused modules are prototypes and must be pruned before production export','native_integration':False,'all96_exhausted':False}
 save('word composer and exact full-support word-tree laws ready')
 data={s:load(s) for s in 'abcd'};train={k:np.concatenate([data[s][k] for s in 'ab']) for k in data['a']};tb={k:torch.as_tensor(v,device='cuda') for k,v in train.items()};dev={k:np.concatenate([data[s][k] for s in 'cd']) for k in data['c']};models={};opts={};steps={}
 for seed in m['contract']['seeds']:
  for kind in m['contract']['arms']:
   key=kind+'_seed'+str(seed);torch.manual_seed(seed);model=Model(kind).cuda();models[key]=model;opts[key]=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=0);steps[key]=0
   sample={k:v[:16].clone() for k,v in tb.items() if k!='y'}
   with torch.no_grad():
    zero=model(**sample,neutral=True);assert torch.equal(zero,sample['p']);a=model(**sample);sample['history'][8:]=1;sample['node'][8:]=0;sample['raw'][8:]=0;assert torch.equal(a[:8],model(**sample)[:8])
 m['zero_native_identity_and_nonzero_future_prefix']='PASS';save('eight word-softmax/composer runs starting')
 survivors=list(models)
 for rung in [128,384,1152]:
  for key in survivors:
   model=models[key];model.train();opt=opts[key];gen=torch.Generator(device='cuda').manual_seed(int(key.split('seed')[-1])+steps[key]*101);start=time.monotonic()
   while steps[key]<rung:
    ix=torch.randint(len(train['y']),(128,),device='cuda',generator=gen);b={k:v[ix] for k,v in tb.items() if k!='y'};opt.zero_grad(set_to_none=True);q=model(**b);F.binary_cross_entropy(q,tb['y'][ix]).backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();steps[key]+=1
    if steps[key]%64==0:save(key+' step'+str(steps[key]))
   result=score(model,dev);path=S/(key+'_step'+str(rung)+'.pt');torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'steps':rung,'key':key},path);weights=b''.join(v.detach().cpu().numpy().tobytes() for v in model.state_dict().values());m['rungs'].append({'key':key,'step':rung,'development':result,'training_seconds_this_rung':time.monotonic()-start,'parameters':sum(v.numel() for v in model.parameters()),'zlib9_unpruned_state_bytes':len(zlib.compress(weights,9)),'checkpoint_path':str(path),'checkpoint_sha256':sha(path)});save(key+' rung'+str(rung)+' complete')
  if rung<1152:
   survivors=[]
   for seed in m['contract']['seeds']:
    rows=[v for v in m['rungs'] if v['step']==rung and v['key'].endswith('seed'+str(seed))];rows.sort(key=lambda v:v['development']['gain_vs_adaptive_bytes'],reverse=True);survivors.extend(v['key'] for v in rows[:2 if rung==128 else 1])
   m.setdefault('frozen_selections',[]).append({'rung':rung,'survivors':survivors});save('development-only word-head selection frozen')
 m['frozen_finalists']=survivors;save('word-head finalists frozen before E/F')
 for s in 'ef':
  rec=load(s)
  for key in survivors:m['confirmation'].append({'slice':s,'key':key,'result':score(models[key],rec)});save(key+' '+s+' confirmation')
 m.update(status='COMPLETE_EXACT_WORD_SOFTMAX_AND_SPELLING_COMPOSER_SCREEN',finished=time.time(),full_or_native_package_qualified=False);save('word-level architecture tested; exact native integration and costs remain open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
