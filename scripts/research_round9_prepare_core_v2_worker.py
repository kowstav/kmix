"""Resume only successful alignment/import; repair neural input framing.

The original failed worker and its outputs remain unchanged.
"""
import pathlib,json,time,traceback,subprocess,os,hashlib
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'full_word_alignment_v2';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/core_data_v2');S.mkdir(exist_ok=False);old=pathlib.Path('/root/hp_round9/core_data_v1');T=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree');m={'status':'RUNNING','pid':os.getpid(),'start':time.time(),'deletions':[],'repair':'exclude outer type/decoded-length/dictionary-mode header from neural payload; retain byte-to-word alignment by exact offset','alignment_v1_preserved':True}
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 raw=(old/'input.bin').read_bytes();assert raw[0]==7 and raw[5]==7
 payload=raw[6:];bm=pathlib.Path('/kaggle/working/hp_round7/preserved/data/vocab.bm').read_bytes();allowed={i for i in range(256) if (bm[i//8]>>(i%8))&1};assert len(allowed)==205;assert set(payload)<=allowed,sorted(set(payload)-allowed)
 (S/'input.bin').write_bytes(payload);np.fromfile(old/'word_frequency.i32','<i4')[6:].tofile(S/'word_frequency.i32');(S/'lex_weights.bin').symlink_to(old/'lex_weights.bin');(S/'.dict').symlink_to(T/'dictionary/english.dic');m['alignment']=json.loads((R/'full_word_alignment_v1/manifest.json').read_text())['alignment'];m['input_outer_header_bytes']=6;m['target_bytes']=len(payload)
 # Decoder-reachable article resets are encoded separator completions, same as
 # Predictor/lstm separator. Outer headers have their own classical fallback.
 dictionary=__import__('re').findall('[a-z]+',(T/'dictionary/english.dic').read_text())
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
  return bytes(map(inv,v))
 marker=b''.join(code(dictionary.index(w)) if w.isalpha() else bytes([inv(ord(w))]) for w in __import__('re').findall('[a-z]+|[^a-z]','  <page>\n    <title>'))
 ends=[p.end() for p in __import__('re').finditer(__import__('re').escape(marker),payload)];bounds=np.array(sorted(set([0,*ends,len(payload)])),np.int32);bounds.tofile(S/'bounds.i32');m['boundaries']=len(bounds);m['marker_hex']=marker.hex()
 env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};env.update(LAB_RAW='1',LAB_VOCAB='/kaggle/working/hp_round7/preserved/data/vocab.bm',LAB_DICT=str(T/'dictionary/english.dic'),LAB_KEEP_TEMP='1');save('running current selected native model on framed payload')
 cmd=[str(T/'cmix'),'-n','--transformer-only','--transformer',str(T/'models/lex_h1_run11.tfwc2'),'--save-ppmd-bytes',str(S/'tokens.u8'),'--save-ppmd-probs',str(S/'priors.f16'),'--save-transformer-probs',str(S/'native_nn.f16'),str(S/'input.bin'),str(S/'native_control.cmx')]
 t=time.monotonic()
 with (D/'native_prior.log').open('w') as f:p=subprocess.Popen(cmd,cwd=S,env=env,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 m['native_accounting']={'seconds':time.monotonic()-t,'CPU_user_seconds':u.ru_utime,'CPU_system_seconds':u.ru_stime,'peak_RSS_KiB':u.ru_maxrss,'returncode':p.returncode};assert p.returncode==0
 assert (S/'priors.f16').stat().st_size==len(payload)*205*2
 m['files']=[{'path':str(S/n),'bytes':(S/n).stat().st_size,'sha256':sha(S/n)} for n in ['input.bin','tokens.u8','priors.f16','native_nn.f16','word_frequency.i32','lex_weights.bin','native_control.cmx','bounds.i32']];m.update(status='COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS',finish=time.time(),scratch=str(S));save('full words including literals/OOVs and native priors ready')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
