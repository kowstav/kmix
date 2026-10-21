"""Stronger word-cache descendant: before-target contextual/difficulty gating.

Reuse all completed expert files. A global zero mixture does not settle a
specialist active only during a dictionary continuation or a difficult bit.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import pathlib,json,time,traceback,hashlib,ast,math
import numpy as np
from scipy.special import expit
from scipy.optimize import brentq
from numba import njit
R=pathlib.Path('/kaggle/working/hp_round8');OUT=pathlib.Path('/kaggle/working/hp_round9');D=OUT/'word_cache_gated_v2';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[],'development':[],'confirmation':[]}
def save(s):m['stage']=s;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(s,flush=True)
def unpermute(c):
 c=c.copy().astype(np.int16);original=c.copy();ix=(original>=123)&(original<127);c[ix]-=43;ix=(original>=80)&(original<84);c[ix]+=43
 ix=((c>=58)&(c<=63))|((c>=74)&(c<=79));c[ix]^=112;ix=(c==88)|(c==96);c[ix]^=56;return c
try:
 assert json.loads((OUT/'word_cache_v2/manifest.json').read_text())['status'].startswith('COMPLETE')
 tree=ast.parse((OUT/'research_round9_adaptive_source_worker.py').read_text());ns={'np':np,'math':math,'njit':njit};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='replay'],type_ignores=[]),'<adaptive-replay>','exec'),ns);replay=ns['replay']
 tree=ast.parse((OUT/'research_round9_title_memory_worker.py').read_text());ns={'np':np,'R':R,'replay':replay,'expit':expit};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load'],type_ignores=[]),'<unchanged-reference>','exec'),ns);load_native=ns['load']
 keys=[(law,kind,hard) for law in range(8) for kind in ['all','dictionary_continuation','literal_letters','separators'] for hard in [False,True]]
 m['contract']={'laws':keys,'fit':'64scalar convex MLEs,ABfit,CDselect including identity,freeze before EF','gates':'before-byte inverse-permuted previous symbol; dictionary ongoing lead208..255,literal ASCII letters/apostrophe,separators; optional before-bit adaptive p in[.1,.9]; every gate available before target','nuance':'dictionary gate is a causal lexical heuristic; exact native parser required for promotion; no future difficulty labels','inheritance':'existing cache experts and zero identity/nonzero prefix controls reused; gated mapping adds its own future-prefix proof','price':'selected scalar8B per copy plus parser/rule code and bounded cache; no native/package result inferred'}
 def byte_gates(raw):
  c=unpermute(np.frombuffer(raw,'u1'));prev=np.r_[-1,c[:-1]];return {'all':np.arange(len(c))>=16,'dictionary_continuation':(prev>=208)&(np.arange(len(c))>=16),'literal_letters':(((prev>=97)&(prev<=122))|((prev>=65)&(prev<=90))|(prev==39))&(np.arange(len(c))>=16),'separators':np.isin(prev,[32,9,10,13,44,46,59,58])&(np.arange(len(c))>=16)}
 allbytes=np.arange(256,dtype=np.uint8);assert np.array_equal(unpermute(unpermute(allbytes).astype(np.uint8)),allbytes);m['inverse_permutation_exhaustive_involution']='PASS'
 probe=b' abc de xyz qqq vvv ttt';cut=18;g=byte_gates(probe);h=byte_gates(probe[:cut]+b'zzzzzzzzzz')
 assert all(np.array_equal(g[k][:cut],h[k][:cut]) for k in g);m['gated_future_prefix']='PASS'
 def load(s):
  raw,base,y=load_native(s);path=pathlib.Path('/root/hp_round9/word_cache_v2')/(s+'.u16');assert path.stat().st_size==len(raw)*128;expert=np.memmap(path,'<u2','r',shape=(len(base),8));g=byte_gates(raw);return {'raw':raw,'base':base.astype(np.int64),'y':y,'expert':expert,'gates':{k:np.repeat(v,8) for k,v in g.items()},'hard':(base>=6554)&(base<=58982)}
 ab=[load(s) for s in 'ab'];coeff={}
 for law,kind,hard in keys:
  parts=[]
  for rec in ab:
   active=rec['gates'][kind]&(rec['hard'] if hard else True);y=rec['y'][active];b=rec['base'][active];q=rec['expert'][:,law][active].astype(np.int64);bp=np.where(y,b,65536-b);ep=np.where(y,q,65536-q);parts.append((ep-bp)/bp)
  r=np.concatenate(parts);f=lambda a:float((r/(1+a*r)).sum());coeff[str((law,kind,hard))]=0. if not len(r) or f(0)<=0 else .5 if f(.5)>=0 else float(brentq(f,0,.5,xtol=1e-12))
 del ab;m['frozen_coefficients_before_CD']=coeff;save('all before-target specialist coefficients fitted on AB')
 def score(rec,key):
  law,kind,hard=key;a=coeff[str(key)];active=rec['gates'][kind]&(rec['hard'] if hard else True);b=rec['base'];e=rec['expert'][:,law].astype(np.int64);q=np.clip(np.floor(b+a*active*(e-b)+.5),1,65535).astype(np.int64);y=rec['y'];return {'gain_vs_adaptive_bytes':float(np.log2(np.where(y,q,65536-q)/np.where(y,b,65536-b)).sum()/8),'Q16_sha256':hashlib.sha256(q.astype('<u2').tobytes()).hexdigest(),'active_bits':int(active.sum())}
 for s in 'cd':
  rec=load(s)
  for key in keys:m['development'].append({'slice':s,'key':key,'alpha':coeff[str(key)],'result':score(rec,key)})
  save(s+'64 contextual cache laws scored')
 rank=sorted(keys,key=lambda key:sum(v['result']['gain_vs_adaptive_bytes'] for v in m['development'] if tuple(v['key'])==key)-16,reverse=True);m['frozen_finalists_before_EF']=rank[:2];save('CD frozen contextual finalists')
 for s in 'ef':
  rec=load(s)
  for key in rank[:2]:m['confirmation'].append({'slice':s,'key':key,'alpha':coeff[str(key)],'result':score(rec,key)})
  save(s+' contextual cache confirmation')
 m.update(status='COMPLETE_CONTEXT_GATED_WORD_DONOR_CACHE_REPLAY',finished=time.time(),native_or_full_package_qualified=False);save('stronger no-retraining context-gated descendant complete')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
