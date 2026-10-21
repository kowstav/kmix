"""Exact full-prefix WRT decode, emitting only causal complete-word events.

A word enters history after its delimiter's encoded bytes are complete. Events
crossing a cold slice's start/end are excluded. No frequency/rarity labels become
inputs. Independently compares every decoded byte to the native decoder.
"""
import pathlib,os,time,json,subprocess,traceback,hashlib
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'word_events_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/word_events_v1');S.mkdir(exist_ok=False);T=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree')
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scope':'exact completed-word events for six matched native cold slices','spending_usd':0,'deletions':[],'scratch':str(S)}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while c:=f.read(1<<20):h.update(c)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
try:
 offsets={'a':0,'b':102635191,'c':310000000,'d':520000000,'e':190000000,'f':430000000};m['windows']=[{'slice':s,'start':v,'end':v+524288} for s,v in offsets.items()];(S/'windows.txt').write_text(''.join(f'{v} {v+524288}\n' for v in offsets.values()))
 source=R/'research_round9_word_events.cpp';m['source_sha256']=sha(source)
 subprocess.run(['clang++-17','-O2','-std=c++17','-march=x86-64-v3','-mrecip=none','-I'+str(T/'src/preprocess'),str(source),str(T/'src/preprocess/dictionary.cpp'),'-o',str(S/'word_events')],check=True)
 cmd=[str(S/'word_events'),'/kaggle/working/hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt',str(T/'dictionary/english.dic'),str(S/'events.tsv'),str(S/'sample.txt'),str(max(v+524288 for v in offsets.values())),str(S/'windows.txt')];save('independent native character verification and completed-event extraction through D slice')
 start=time.monotonic()
 with (D/'decode.log').open('w') as f:p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 m['accounting']={'wall_seconds':time.monotonic()-start,'CPU_seconds':u.ru_utime+u.ru_stime,'peak_RSS_KiB':u.ru_maxrss,'returncode':p.returncode};assert p.returncode==0
 m['native_decode_comparison']=json.loads((D/'decode.log').read_text());counts={s:0 for s in offsets}
 for line in (S/'events.tsv').open():
  idx,lo,hi,completion,body,word=line.rstrip().split('\t');window=m['windows'][int(idx)];assert int(lo)>=window['start']+16 and int(completion)<=window['end'] and int(hi)<=int(completion);counts[window['slice']]+=1
 m.update(status='COMPLETE_CAUSAL_WHOLE_WORD_EVENTS',finished=time.time(),event_counts=counts,event_file_bytes=(S/'events.tsv').stat().st_size,event_file_sha256=sha(S/'events.tsv'),input_features='complete word strings and delimiter completion positions only; intext labels are unused by predictors');save('complete-word event positions verified; causal feature builders may proceed')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
