"""No-retraining completed-word cache: spelling/placement/TTL actual output laws.

Fit only eight scalar nonnegative mixture coefficients; all donor state is causal
and reconstructed from completed decoded words. This is finite cold replay, not
an independently native-decoded compressor. Exact production parsing is pending.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import pathlib,json,time,hashlib,traceback,ast,subprocess,math
import numpy as np
from scipy.optimize import brentq
from numba import njit
R=pathlib.Path('/kaggle/working/hp_round8');OUT=pathlib.Path('/kaggle/working/hp_round9');D=OUT/'word_cache_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/word_cache_v1');S.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[],'scratch':str(S),'development':[],'confirmation':[]}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd):
 t=time.monotonic();p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);o,e=p.communicate();assert p.returncode==0,(cmd,e.decode());return {'wall_seconds':time.monotonic()-t,'stdout':o.decode()}
try:
 tree=ast.parse((OUT/'research_round9_adaptive_source_worker.py').read_text());ns={'np':np,'math':math,'njit':njit};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='replay'],type_ignores=[]),'<adaptive-replay>','exec'),ns);replay=ns['replay']
 tree=ast.parse((OUT/'research_round9_title_memory_worker.py').read_text());ns={'np':np,'R':R,'replay':replay};from scipy.special import expit;ns['expit']=expit;exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load'],type_ignores=[]),'<unchanged-adaptive-reference>','exec'),ns);load=ns['load']
 eventmanifest=json.loads((OUT/'word_events_v1/manifest.json').read_text());assert eventmanifest['status']=='COMPLETE_CAUSAL_WHOLE_WORD_EVENTS';rows=[[] for _ in range(6)]
 for line in pathlib.Path(eventmanifest['scratch'],'events.tsv').open():
  idx,lo,hi,at,body,word=line.rstrip().split('\t');rows[int(idx)].append((int(lo),int(hi),int(at),word))
 m['contract']={'laws':['count','recency8','recency64','recency256','constructor_context','letter_bag_cosine4','first_letter','constructor_letter_bag_last_letter'],'state':'last256 completed encoded word spans,length1..64bytes; longest matching proper encoded-word prefix among last8alreadydecodedbytes; donors available only after delimiter completion','placement':'donor preceding completed-word constructor class vs current previous-word class; heuristic constructor lexicon,not POS truth','structural':'past-word letter bags/first-last letters; no claim that diamond implies almond or that anagrams share meaning','TTL':'donor age in completed words; recency8/64/256,rolling256word eviction; much longer than earlier128byte reset in many contexts','fit':'one scalar alpha per law MLE on A/B,0<=alpha<=.5; C/D selection including identity; freeze before E/F','support':'counted next encoded donor byte+.001Dirichlet over256bytes,conditional on alreadyknown bit prefix; expert Q16 first,then integer mixture','price':'8B coefficient per selected law per counted copy plus rule/parser/code/memory; executable unmeasured','native':'read-only replay; actual decoder must reproduce full semantic framing and events before promotion'}
 binary=S/'word_cache';m['build']=run(['g++','-O3','-std=c++17',str(OUT/'research_round9_word_cache.cpp'),'-o',str(binary)]);m['binary_sha256']=sha(binary);m['source_sha256']=sha(OUT/'research_round9_word_cache.cpp');save('eight real word donor laws compiled')
 # Deliberately nonzero cache test: only completed prefix events may influence it.
 toy=b'abc def abc def abc def xyz';events='0 3 4 abc\n4 7 8 def\n8 11 12 abc\n';(S/'toy.events').write_text(events);(S/'toy.bin').write_bytes(toy);run([str(binary),str(S/'toy.bin'),str(S/'toy.events'),str(S/'toy.q')]);cut=19;(S/'toy_mutated.bin').write_bytes(toy[:cut]+b'zzzzzzzz');run([str(binary),str(S/'toy_mutated.bin'),str(S/'toy.events'),str(S/'toy_mutated.q')]);assert (S/'toy.q').read_bytes()[:cut*128]==(S/'toy_mutated.q').read_bytes()[:cut*128];m['nonzero_future_prefix']='PASS'
 def features(s,raw):
  window=next(v for v in eventmanifest['windows'] if v['slice']==s);start=window['start'];events=[(lo-start,hi-start,at-start,w) for lo,hi,at,w in rows['abcdef'.index(s)]];ep=S/(s+'.events');ep.write_text(''.join(f'{lo} {hi} {at} {w}\n' for lo,hi,at,w in events));rp=S/(s+'.bin');rp.write_bytes(raw);qp=S/(s+'.u16');account=run([str(binary),str(rp),str(ep),str(qp)]);assert qp.stat().st_size==len(raw)*128;active=np.arange(len(raw))>=min([e[2] for e in events],default=len(raw));m.setdefault('features',[]).append({'slice':s,'raw_sha256':sha(rp),'events_sha256':sha(ep),'Q16_sha256':sha(qp),'accounting':account});save(s+' causal word laws generated');return np.memmap(qp,'<u2','r',shape=(len(raw)*8,8)),np.repeat(active,8)
 rs=[[] for _ in range(8)]
 for s in 'ab':
  raw,base,y=load(s);q,active=features(s,raw);bp=np.where(y,base,65536-base).astype(np.float64)[active]
  for law in range(8):ep=np.where(y,q[:,law],65536-q[:,law]).astype(np.float64)[active];rs[law].append((ep-bp)/bp)
 coefficients=[]
 for parts in rs:
  r=np.concatenate(parts);f=lambda a:float((r/(1+a*r)).sum());a=0. if not len(r) or f(0.)<=0 else .5 if f(.5)>=0 else float(brentq(f,0,.5,xtol=1e-12));coefficients.append(a)
 del rs;m['frozen_coefficients_before_CD']=coefficients;save('all scalar cache mixtures frozen before development')
 def score(base,y,q,active,a):
  mixed=np.clip(np.floor((1-a*active)*base.astype(np.float64)+a*active*q.astype(np.float64)+.5),1,65535).astype('<u2');py=np.where(y,mixed,65536-mixed).astype(np.float64);bp=np.where(y,base,65536-base).astype(np.float64);return {'gain_vs_adaptive_bytes':float(np.log2(py/bp).sum()/8),'Q16_sha256':hashlib.sha256(mixed.tobytes()).hexdigest()}
 # Explicit integer identity, not a floating-loss approximation.
 raw,base,y=load('a');assert score(base,y,np.full(len(base),32768,'<u2'),np.ones(len(base)),0.)['Q16_sha256']==hashlib.sha256(base.tobytes()).hexdigest();m['zero_identity']='PASS'
 for s in 'cd':
  raw,base,y=load(s);q,active=features(s,raw)
  for law in range(8):m['development'].append({'slice':s,'law':law,'alpha':coefficients[law],'result':score(base,y,q[:,law],active,coefficients[law])})
  save(s+' all word-cache laws scored')
 rank=sorted(range(8),key=lambda k:sum(v['result']['gain_vs_adaptive_bytes'] for v in m['development'] if v['law']==k)-16,reverse=True);m['frozen_finalists_before_EF']=rank[:2];m['identity_development_gain_bytes']=0.;save('two finite cache finalists frozen before E/F')
 for s in 'ef':
  raw,base,y=load(s);q,active=features(s,raw)
  for law in rank[:2]:m['confirmation'].append({'slice':s,'law':law,'alpha':coefficients[law],'result':score(base,y,q[:,law],active,coefficients[law])})
  save(s+' word-cache confirmation')
 m.update(status='COMPLETE_COMPLETED_WORD_DONOR_CACHE_REPLAY',finished=time.time(),native_or_full_package_qualified=False);save('finite no-retraining spelling/placement/cache laws complete')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
