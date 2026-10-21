import pathlib,json,hashlib,subprocess,time,traceback,os,sys,gzip
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'full_word_alignment_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/core_data_v1');S.mkdir(exist_ok=False);T=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree');m={'status':'RUNNING','pid':os.getpid(),'start':time.time(),'deletions':[],'spending_usd':0,'results':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def run(cmd,label):
 t=time.monotonic()
 with (D/(label+'.log')).open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,cwd=S)
 m['results'].append({'label':label,'returncode':p.returncode,'seconds':time.monotonic()-t});save(label);assert p.returncode==0,(label,p.returncode)
try:
 save('compiling exact native weight importer and independently checked full-word decoder')
 run(['g++','-O2','-std=c++17','-I'+str(T/'src/preprocess'),str(R/'research_round9_word_alignment.cpp'),str(T/'src/preprocess/dictionary.cpp'),'-o',str(S/'word_alignment')],'build_alignment')
 run(['g++','-O2','-std=c++17','-I'+str(T/'cpp_infer/src'),str(R/'research_round9_weights_dump.cpp'),str(T/'cpp_infer/src/weights_io.cpp'),str(T/'cpp_infer/src/weights_io_compressed.cpp'),'-o',str(S/'weights_dump')],'build_weight_import')
 run([str(S/'weights_dump'),str(T/'models/lex_h1_run11.tfwc2'),str(S/'lex_weights.bin')],'export_actual_packed_lex_tensors')
 stream=pathlib.Path('/kaggle/working/hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt')
 with stream.open('rb') as f:raw=f.read(262144)
 (S/'input.bin').write_bytes(raw);run([str(S/'word_alignment'),str(stream),str(T/'dictionary/english.dic'),str(S/'word_events.tsv'),str(D/'decoded_sample.txt'),'270000'],'annotated_vs_native_decode')
 counts={}
 with gzip.open('/kaggle/working/hp_round8/rarity_census_v1/word_article_frequencies.tsv.gz','rt') as f:
  next(f)
  for line in f:w,c,*rest=line.rstrip('\n').split('\t');counts[w]=int(c)
 frequency=np.full(len(raw),-1,np.int32);word_events=body_events=literal_body_bytes=0;dictionary_words=set(__import__('re').findall('[a-z]+',(T/'dictionary/english.dic').read_text()));event_details=[]
 with (S/'word_events.tsv').open() as f:
  for line in f:
   lo,hi,body,w=line.rstrip('\n').split('\t');lo=int(lo);hi=int(hi);word_events+=1
   if int(body) and hi<=len(raw):frequency[lo:hi]=counts.get(w,0);body_events+=1;literal_body_bytes+=((hi-lo) if w not in dictionary_words else 0);event_details.append([lo,hi,w,counts.get(w,0),w in dictionary_words])
 frequency.tofile(S/'word_frequency.i32');(D/'word_event_details.json').write_text(json.dumps(event_details));m['alignment']={'supervision':'full decoded whole ASCII words in transformed XML text body; case markers, literal bytes and encoded substrings assigned together; no labels enter model input','word_events':word_events,'body_word_events':body_events,'labelled_bytes':int(np.sum(frequency>=0)),'non_dictionary_whole_word_bytes':literal_body_bytes,'metadata_control_whitespace_side':'unmasked default weight1','terminal_crossing_word':'unlabelled; decoded through270000 to cover262144 target prefix','frequency_source':'original decoded enwik9 text census; transformed spellings absent from census count0','raw_sha256':sha(S/'input.bin'),'labels_sha256':sha(S/'word_frequency.i32')}
 assert body_events>1000 and literal_body_bytes>0
 env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};env.update(LAB_RAW='1',LAB_VOCAB='/kaggle/working/hp_round7/preserved/data/vocab.bm',LAB_DICT=str(T/'dictionary/english.dic'),LAB_KEEP_TEMP='1')
 binary=T/'cmix';assert binary.exists();save('generating current canonical full205 native PPMD priors and neural comparison')
 args=[str(binary),'-n','--transformer-only','--transformer',str(T/'models/lex_h1_run11.tfwc2'),'--save-ppmd-bytes',str(S/'tokens.u8'),'--save-ppmd-probs',str(S/'priors.f16'),'--save-transformer-probs',str(S/'native_nn.f16'),str(S/'input.bin'),str(S/'native_control.cmx')]
 t=time.monotonic()
 with (D/'native_prior.log').open('w') as f:p=subprocess.Popen(args,cwd=S,env=env,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 assert p.returncode==0;m['native_accounting']={'seconds':time.monotonic()-t,'CPU_user_seconds':u.ru_utime,'CPU_system_seconds':u.ru_stime,'peak_RSS_KiB':u.ru_maxrss}
 assert (S/'priors.f16').stat().st_size==len(raw)*205*2
 m['files']=[{'path':str(S/n),'bytes':(S/n).stat().st_size,'sha256':sha(S/n)} for n in ['input.bin','tokens.u8','priors.f16','native_nn.f16','word_frequency.i32','lex_weights.bin','native_control.cmx']]
 m.update(status='COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS',finish=time.time(),scratch=str(S));save('full literal/OOV labels and actual selected model tensors ready')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
