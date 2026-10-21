"""No-retraining persistent article-title copy law, with normalized bit support.

Titles are collected only after their encoded bytes have appeared. They stay
available until the next title/page end, exceeding a short transformer window.
This is an actual byte-copy probability law, not a hidden similarity proxy.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import pathlib,json,time,hashlib,traceback,re,ast,math
import numpy as np
from scipy.special import expit
from scipy.optimize import brentq
from numba import njit
R=pathlib.Path('/kaggle/working/hp_round8');OUT=pathlib.Path('/kaggle/working/hp_round9');D=OUT/'title_memory_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[],'development':[],'confirmation':[],'scope':'causal persistent title substring-copy laws; only native integer baseline/source history and already observed title bytes'}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inv(c):
 if 123<=c<127:c-=43
 elif 80<=c<84:c+=43
 elif 58<=c<=63 or 74<=c<=79:c^=112
 if c in [88,96]:c^=56
 return c
def code(j):
 if j<80:v=[128+j]
 elif j<3920:j-=80;v=[208+j//80,128+j%80]
 else:j-=3920;v=[240+(j//80)//32,208+(j//80)%32,128+j%80]
 return bytes(inv(x) for x in v)
def title_features(raw,kind,open_tag,close_tag,page_end):
 n=len(raw);expert=np.full((n,8),.5,np.float32);active=np.zeros(n,bool);title=bytearray();collecting=False;history=bytearray();tables={};title_bytes=0;max_title=0
 lengths=[0] if kind=='histogram' else [int(kind[1:])] if kind!='longest' else [8,4,2,1]
 for i,b in enumerate(raw):
  # Predict with completed past bytes, then reveal this byte bit by bit.
  counts=None
  if tables and not collecting:
   for L in lengths:
    key=bytes(history[-L:]) if L else b''
    if L and len(key)!=L:continue
    if (L,key) in tables:counts=tables[(L,key)];break
  if counts:
   items=list(counts.items());total=sum(v for _,v in items);prefix=0
   for bit in range(8):
    keepmask=0xff^(0xff>>bit);den=.001*(256>>bit);num=.001*(128>>bit)
    for value,count in items:
     if value&keepmask==prefix:
      den+=count
      if (value>>(7-bit))&1:num+=count
    expert[i,bit]=num/den
    # Only bits preceding the next prediction become part of its prefix.
    prefix|=((int(b)>>(7-bit))&1)<<(7-bit)
   active[i]=True
  history.append(int(b))
  if len(history)>64:del history[:-64]
  if collecting:
   title.append(int(b))
   if len(title)>4096+len(close_tag):collecting=False;title.clear();tables={}
  if history.endswith(open_tag):collecting=True;title.clear();tables={}
  elif collecting and history.endswith(close_tag):
   del title[-len(close_tag):];collecting=False;tables={};max_title=max(max_title,len(title));title_bytes+=len(title)
   for L in lengths:
    for at in range(L,len(title)):
     key=(L,bytes(title[at-L:at]));entry=tables.setdefault(key,{});v=int(title[at]);entry[v]=entry.get(v,0)+1
  elif history.endswith(page_end):tables={};title.clear();collecting=False
 return expert,active,{'active_byte_contexts':int(active.sum()),'completed_title_bytes':title_bytes,'max_stored_title_bytes':max_title}
def load(s):
 N=R/'atom_cache_v1';root=(R/'native_stage_trace_v1' if s in 'ab' else R/'native_stage_weak_confirmation_v1' if s in 'cd' else R/'source_wide_confirmation_v1')/(s+'512k');rawpath=N/(s+'512k.bin') if s in 'abcd' else root/'input.bin';raw=rawpath.read_bytes();pp=N/(s+'_native/final_p.u16') if s in 'abcd' else root/'final_p.u16';native=np.fromfile(pp,'<u2');ell=np.log(native.astype(np.float64)/(65536-native.astype(np.float64)));hp=N/(s+'_native/hidden.q8') if s in 'abcd' else root/'hidden.q8';h=np.memmap(hp,'u1','r',shape=(len(raw),193));valid=np.repeat(np.r_[0,h[:-1,0]],8);st=np.memmap(root/'stage.f32','<f4','r',offset=12,shape=(len(native),19));nn=np.clip(st[:,17].astype(np.float64),1/65536,65535/65536);f=(np.clip(np.log(nn/(1-nn))-ell,-12,12)/12).astype(np.float32)*valid;f=f.astype(np.float64);delta=.0016181118716570748-.007454085408717222*ell+2.3818512619982752*f;y=((np.frombuffer(raw,'u1')[:,None]>>(7-np.arange(8)))&1).reshape(-1).astype('u1');experts=np.column_stack([native,*[np.clip(np.floor(65536*expit(ell+a*delta)+.5),1,65535).astype('<u2') for a in [.5,1.,1.5,2.]]]);q=replay(experts,y,2.6441431586476938e-06)[0];return raw,q,y
def ratios(base,y,expert,active):
 p=base.astype(np.float64)/65536;ix=np.repeat(active,8);py=np.where(y[ix],p[ix],1-p[ix]);e=expert.reshape(-1).astype(np.float64)[ix];ey=np.where(y[ix],e,1-e);return (ey-py)/py
def fit(rs):
 r=np.concatenate(rs)
 if not len(r) or r.sum()<=0:return 0.
 fun=lambda a:float((r/(1+a*r)).sum())
 return .5 if fun(.5)>=0 else float(brentq(fun,0,.5,xtol=1e-12))
def measure(base,y,expert,active,alpha):
 p=base.astype(np.float64)/65536;e=expert.reshape(-1).astype(np.float64);a=alpha*np.repeat(active,8);q=np.clip(np.floor(65536*((1-a)*p+a*e)+.5),1,65535).astype('<u2');sel=np.where(y,q.astype(np.float64),65536-q.astype(np.float64));old=np.where(y,base.astype(np.float64),65536-base.astype(np.float64));return {'gain_vs_adaptive_bytes':float(np.log2(sel/old).sum()/8),'Q16_sha256':hashlib.sha256(q.tobytes()).hexdigest(),'active_contexts':int(active.sum())}
try:
 rt=ast.parse((OUT/'research_round9_adaptive_source_worker.py').read_text());ns={'np':np,'math':math,'njit':njit};exec(compile(ast.Module(body=[n for n in rt.body if isinstance(n,ast.FunctionDef) and n.name=='replay'],type_ignores=[]),'<adaptive-replay>','exec'),ns);replay=ns['replay'];words=re.findall('[a-z]+',(R/'native_stage_trace_v1/tree/dictionary/english.dic').read_text());assert len(words)==44515;lookup={w:i for i,w in enumerate(words)}
 def encoded(s):return b''.join(code(lookup[w]) if w.isalpha() else bytes([inv(ord(w))]) for w in re.findall('[a-z]+|[^a-z]',s))
 tags=[encoded(s) for s in ['<title>','</title>','</page>']];kinds=['histogram','L1','L2','L4','L8','longest'];m['contract']={'laws':kinds,'alpha':'one convex MLE coefficient/law,0<=alpha<=.5,fit all eligible A/B bit contexts; state/mixture never sees future labels','normalization':'observed-title next-byte counts plus.001Dirichlet smoothing over256bytes; conditionalize on already-known current bit prefix','lifetime':'until next completed title-open tag or page-end; max4096stored title bytes; no1024byte TTL truncation','decode':'production full semantic framing/native parser and eligible memory/time still required; literal tag collisions possible outside known semantic WRT mode','price':'one8B coefficient per copy plus selected rule code; native executable/memory cost unmeasured; coefficients alone are not the full price','data':'ABfit; CDselection; EFfit-held-out confirmation, previously viewed by other families'};m['worker_sha256']=sha(OUT/'research_round9_title_memory_worker.py')
 toy=tags[0]+encoded('a diamond')+tags[1]+b' '+encoded('a diamond')*3;cut=len(toy)-5
 for kind in kinds:
  e,a,_=title_features(toy,kind,*tags);f,b,_=title_features(toy[:cut]+b'zzzzz',kind,*tags);assert np.array_equal(e[:cut],f[:cut]) and np.array_equal(a[:cut],b[:cut]);native=np.full(len(toy)*8,32768,'<u2');y=((np.frombuffer(toy,'u1')[:,None]>>(7-np.arange(8)))&1).reshape(-1);assert measure(native,y,e,a,0.)['gain_vs_adaptive_bytes']==0
 m['nonzero_future_prefix_and_zero_identity']='PASS';save('persistent title copy laws causal and normalized')
 rs={k:[] for k in kinds}
 for s in 'ab':
  raw,base,y=load(s)
  for kind in kinds:
   e,a,meta=title_features(raw,kind,*tags);rs[kind].append(ratios(base,y,e,a));m.setdefault('development_feature_counts',[]).append({'slice':s,'law':kind,**meta})
  save('title '+s+' fit observations ready')
 coefficients={k:fit(rs[k]) for k in kinds};m['frozen_coefficients_before_CD']=coefficients;del rs;save('title mixture laws frozen')
 for s in 'cd':
  raw,base,y=load(s)
  for kind in kinds:
   e,a,meta=title_features(raw,kind,*tags);m['development'].append({'slice':s,'law':kind,'alpha':coefficients[kind],'result':measure(base,y,e,a,coefficients[kind]),'features':meta})
  save('title '+s+' development')
 rank=sorted(kinds,key=lambda k:sum(v['result']['gain_vs_adaptive_bytes'] for v in m['development'] if v['law']==k)-16,reverse=True);m['frozen_finalists_before_EF']=rank[:2];save('two title laws selected on CD')
 for s in 'ef':
  raw,base,y=load(s)
  for kind in rank[:2]:
   e,a,meta=title_features(raw,kind,*tags);m['confirmation'].append({'slice':s,'law':kind,'alpha':coefficients[kind],'result':measure(base,y,e,a,coefficients[kind]),'features':meta})
  save('title '+s+' confirmation')
 m.update(status='COMPLETE_CAUSAL_PERSISTENT_TITLE_COPY_REPLAY',finished=time.time(),native_or_full_package_qualified=False);save('title copy descendant replay complete')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
