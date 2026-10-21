"""Distributed, decoder-aligned raw and actually redacted original-core inputs.

Labels never enter the predictor. Priors are regenerated after input redaction;
no original-stream priors are reused for a masked stream. These remain cold
fragment diagnostics, not full warm-history production priors.
"""
import pathlib,json,os,time,hashlib,traceback,subprocess,gzip,re
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'distributed_core_data_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/distributed_core_data_v1');S.mkdir(exist_ok=False)
T=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree');OLD=pathlib.Path('/root/hp_round9/core_data_v2')
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'spending_usd':0,'deletions':[],'scratch':str(S),'slices':[]}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while c:=f.read(1<<20):h.update(c)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def run(cmd,cwd,env,label):
 start=time.monotonic()
 with (D/(label+'.log')).open('w') as f:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,st,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(st)
 v={'wall_seconds':time.monotonic()-start,'CPU_seconds':u.ru_utime+u.ru_stime,'peak_RSS_KiB':u.ru_maxrss,'returncode':p.returncode};assert p.returncode==0,(label,v);return v
try:
 wm=json.loads((R/'word_events_v1/manifest.json').read_text());assert wm['status']=='COMPLETE_CAUSAL_WHOLE_WORD_EVENTS'
 events=pathlib.Path(wm['scratch'])/'events.tsv';assert sha(events)==wm['event_file_sha256'];rows=[[] for _ in range(6)]
 for line in events.open():
  ix,lo,hi,complete,body,w=line.rstrip().split('\t')
  if int(body):rows[int(ix)].append((int(lo),int(hi),w))
 counts={}
 with gzip.open('/kaggle/working/hp_round8/rarity_census_v1/word_article_frequencies.tsv.gz','rt') as f:
  for line in f:
   a=line.rstrip().split('\t')
   if len(a)>1 and a[1].isdigit():counts[a[0]]=int(a[1])
 bm=pathlib.Path('/kaggle/working/hp_round7/preserved/data/vocab.bm').read_bytes();alphabet=[i for i in range(256) if (bm[i//8]>>(i%8))&1];assert len(alphabet)==205
 raw0=(OLD/'input.bin').read_bytes();marker=bytes.fromhex(json.loads((R/'full_word_alignment_v2/manifest.json').read_text())['marker_hex']);dictionary=T/'dictionary/english.dic'
 env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};env.update(LAB_RAW='1',LAB_VOCAB='/kaggle/working/hp_round7/preserved/data/vocab.bm',LAB_DICT=str(dictionary),LAB_KEEP_TEMP='1')
 # Neutral extraction must reproduce the existing neural-input preparation.
 C=S/'neutral';C.mkdir();inp=C/'input.bin';inp.write_bytes(raw0);save('neutral PPMD-only extraction must equal existing native priors')
 acc=run([str(T/'cmix'),'-n','--ppmd-only','--save-ppmd-bytes',str(C/'tokens.u8'),'--save-ppmd-probs',str(C/'priors.f16'),str(inp),str(C/'out.cmx')],C,env,'neutral')
 assert sha(C/'tokens.u8')==sha(OLD/'tokens.u8') and sha(C/'priors.f16')==sha(OLD/'priors.f16')
 m['neutral']={'native_prior_identity':True,'token_identity':True,'accounting':acc};save('PPMD extraction neutral identity PASS')
 for ix,window in enumerate(wm['windows']):
  s=window['slice'];start=window['start'];stream=pathlib.Path('/kaggle/working/hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt')
  with stream.open('rb') as f:f.seek(start);raw=f.read(window['end']-start)
  skip=6 if s=='a' else 0;raw=raw[skip:];start+=skip;assert set(raw)<=set(alphabet),('OOV framing',s,sorted(set(raw)-set(alphabet)))
  freq=np.full(len(raw),-1,np.int32)
  for lo,hi,w in rows[ix]:
   lo-=start;hi-=start
   if lo>=0 and hi<=len(raw):freq[lo:hi]=counts.get(w,0)
  ends=[p.end() for p in re.finditer(re.escape(marker),raw)];assert ends,('no article boundaries',s)
  # First fragment before a known reset is excluded from training/evaluation.
  bounds=np.array([*ends,len(raw)],np.int32);bounds=np.unique(bounds)
  for mode in ['raw','redacted1392']:
   C=S/(s+'_'+mode);C.mkdir();inp=C/'input.bin';data=raw if mode=='raw' else bytes(np.where((freq>=0)&(freq<1392),32,np.frombuffer(raw,'u1')).astype('u1'));inp.write_bytes(data);freq.tofile(C/'word_frequency.i32');bounds.tofile(C/'bounds.i32');save(s+' '+mode+' native priors')
   acc=run([str(T/'cmix'),'-n','--ppmd-only','--save-ppmd-bytes',str(C/'tokens.u8'),'--save-ppmd-probs',str(C/'priors.f16'),str(inp),str(C/'out.cmx')],C,env,s+'_'+mode)
   assert (C/'priors.f16').stat().st_size==len(data)*205*2 and (C/'tokens.u8').stat().st_size==len(data)
   token=np.fromfile(C/'tokens.u8','u1');assert bytes(np.array(alphabet,dtype='u1')[token])==data
   m['slices'].append({'slice':s,'mode':mode,'source_start':start,'target_bytes':len(data),'article_boundaries':len(bounds),'labelled_bytes':int((freq>=0).sum()),'rare1392_bytes':int(((freq>=0)&(freq<1392)).sum()),'accounting':acc,'files':[{'path':str(C/n),'bytes':(C/n).stat().st_size,'sha256':sha(C/n)} for n in ['input.bin','tokens.u8','priors.f16','word_frequency.i32','bounds.i32']]});save(s+' '+mode+' labels and inputs PASS')
 m.update(status='COMPLETE_DISTRIBUTED_RAW_AND_REDACTED_NATIVE_CORE_INPUTS',finished=time.time(),contract={'train':'A/B articles','development':'C/D articles','confirmation':'E/F core-fit-held-out, previously viewed by other families','resets':'complete native article separator ends; first partial article excluded; contexts truncated only as an explicit training diagnostic','labels':'complete body words including literal/OOV/case encoded spans; loss supervision only','priors':'actual native PPMD cold fragment, float16 exactly as original deployed neural input; recomputed separately for redacted1392','scope':'six512KiB fragments, not full corpus or warm history'});save('distributed original-core data ready')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
