"""Actual reversible rare-word input redaction with a priced literal side stream.

Runs unchanged selected weights in the actual combined CM native coder. This
implements a constants-first split, unlike loss-only masking. No future rarity
decision is free: locations, lengths and every original removed byte are coded.
The prototype decoder is Python; eligible executable overhead is still pending.
"""
import pathlib,json,os,time,traceback,hashlib,subprocess,zlib,struct
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'literal_split_v1';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/literal_split_v1');S.mkdir(exist_ok=False);DATA=pathlib.Path('/root/hp_round9/core_data_v2');T=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree')
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scope':'literal/OOV and dictionary rare-word input redaction, constants stream paid, actual final CM encode/decode','spending_usd':0,'deletions':[],'candidates':[],'scratch':str(S)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def vint(n):
 out=bytearray()
 while n>=128:out.append((n&127)|128);n>>=7
 out.append(n);return out
def getv(data,at):
 n=shift=0
 while True:
  b=data[at];at+=1;n|=(b&127)<<shift
  if b<128:return n,at
  shift+=7;assert shift<=63
def split(raw,freq,cutoff):
 mask=(freq>=0)&(freq<cutoff);edges=np.diff(np.r_[False,mask,False].astype(np.int8));starts=np.where(edges==1)[0];ends=np.where(edges==-1)[0];side=bytearray(b'HPMSK1\x00\x00');side+=struct.pack('<I',len(raw));side+=vint(len(starts));prev=0;main=bytearray(raw)
 for lo,hi in zip(starts,ends):side+=vint(int(lo)-prev)+vint(int(hi-lo))+raw[lo:hi];main[lo:hi]=b' '*(hi-lo);prev=int(hi)
 return bytes(main),zlib.compress(bytes(side),9),len(starts),int(mask.sum())
def restore(main,packed):
 side=zlib.decompress(packed);assert side[:8]==b'HPMSK1\x00\x00';length=struct.unpack('<I',side[8:12])[0];assert len(main)==length;count,at=getv(side,12);out=bytearray(main);prev=0
 for _ in range(count):delta,at=getv(side,at);size,at=getv(side,at);lo=prev+delta;hi=lo+size;assert hi<=len(main) and main[lo:hi]==b' '*size;out[lo:hi]=side[at:at+size];at+=size;prev=hi
 assert at==len(side);return bytes(out)
def run(cmd,cwd,env,label):
 t=time.monotonic()
 with (D/(label+'.log')).open('w') as f:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 a={'wall_seconds':time.monotonic()-t,'CPU_seconds':u.ru_utime+u.ru_stime,'peak_RSS_KiB':u.ru_maxrss,'returncode':p.returncode};assert p.returncode==0,(label,a);return a
try:
 m['worker_sha256']=sha(R/'research_round9_literal_split_worker.py');m['contract']={'target_bytes':65536,'thresholds':[107,1392,8372],'rare_policy':'global-frequency supervision controls encoder-side split; decoder receives all positions/lengths/bytes and needs no frequency table','main_mask':'same encoded length, rare byte spans replaced by existing literal-space vocabulary symbol','literal_scope':'all whole body-word dictionary/literal/OOV/case spans in the exact prefix alignment','side_model':'zlib9, not assumed optimal; explicit bitstream','core':'actual selected lexical transformer unchanged','learned_masked-stream_finetuning':'not yet implemented','container_price':'12B framing plus compressed literal stream plus actual native main archive; extra eligible executable decoder code not yet measured','corpus_scope':'65KiB from previously viewed early prefix; diagnostic, not independent corpus confirmation','native_codec':'combined CM final coder, not transformer-only'}
 raw=(DATA/'input.bin').read_bytes()[:65536];freq=np.fromfile(DATA/'word_frequency.i32','<i4')[:len(raw)];dictionary=T/'dictionary/english.dic';weights=pathlib.Path('/kaggle/working/hp_round7/lex_audit/lex_h1_run11.tfwc2');binary=T/'cmix';env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};env.update(LAB_RAW='1',LAB_VOCAB='/kaggle/working/hp_round7/preserved/data/vocab.bm',LAB_DICT=str(dictionary),LAB_KEEP_TEMP='1')
 def encode_decode(name,data):
  C=S/name;C.mkdir();(C/'.dict').symlink_to(dictionary);inp=C/'input.bin';inp.write_bytes(data);out=C/'out.cmx';save(name+' actual combined-CM encode');ea=run([str(binary),'-n','--transformer',str(weights),str(inp),str(out)],C,env,name+'_encode');DE=S/(name+'_decode');DE.mkdir();(DE/'.dict').symlink_to(dictionary);da=run([str(binary),'-d','--transformer',str(weights),str(out),'decoded.bin'],DE,env,name+'_decode');assert (DE/'decoded.bin').read_bytes()==data;return out,DE/'decoded.bin',ea,da
 baseline,decoded,ea,da=encode_decode('baseline',raw);m['baseline']={'archive_bytes':baseline.stat().st_size,'input_sha256':sha(decoded),'independent_decode_exact':True,'encode_accounting':ea,'decode_accounting':da};save('ordinary selected native baseline decode PASS')
 for cutoff in m['contract']['thresholds']:
  main,side,spans,nbytes=split(raw,freq,cutoff);assert restore(main,side)==raw;out,decoded,ea,da=encode_decode('cut'+str(cutoff),main);literal=S/('cut'+str(cutoff)+'.literals.z');literal.write_bytes(side);assert restore(decoded.read_bytes(),literal.read_bytes())==raw
  packed=S/('cut'+str(cutoff)+'.hpmsk');packed.write_bytes(b'HPSPLIT1'+struct.pack('<I',len(side))+side+out.read_bytes());charged=packed.stat().st_size;m['candidates'].append({'cutoff':cutoff,'redacted_bytes':nbytes,'side_spans':spans,'literal_side_bytes':len(side),'native_main_archive_bytes':out.stat().st_size,'container_bytes':charged,'gain_vs_baseline_bytes_before_extra_executable':baseline.stat().st_size-charged,'restored_original_encoded_input_sha256':hashlib.sha256(restore(decoded.read_bytes(),side)).hexdigest(),'exact_restore_and_independent_native_decode':True,'encode_accounting':ea,'decode_accounting':da});save('cut'+str(cutoff)+' split/restore/native gates PASS')
 m.update(status='COMPLETE_REVERSIBLE_LITERAL_INPUT_MASK_SPLIT_NATIVE_SCREEN',finished=time.time(),full_package_qualified=False);save('input-redaction constants split actually tested; masked-stream training and final executable/full corpus remain open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
