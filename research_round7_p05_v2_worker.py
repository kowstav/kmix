import datetime,hashlib,json,os,pathlib,shutil,subprocess,tarfile,traceback,zipfile
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round7');D=R/'full_stream_regen_v2';W=pathlib.Path('/root/hp/full_stream_regen_v2')
assert not D.exists() and not W.exists();D.mkdir();W.mkdir(parents=True)
m={'status':'RUNNING','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':os.getpid(),'deletions':[],'paid_rental_usd':0,
 'repair':'v1 inspected compressed executable strings; absence did not establish absence of flags. v2 uses explicit --bytes-only; unknown flags fail before model execution.', 'scratch':str(W)}
def save():(D/'manifest.json').write_text(json.dumps(m,indent=2))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
save()
try:
 with tarfile.open(R/'preserved/research_sources_and_candidates.tar.gz') as t:
  (W/'cmix').write_bytes(t.extractfile('cand_final2/run/cmix').read());(W/'cmix').chmod(0o755)
 with zipfile.ZipFile(R/'preserved/data/enwik9.zip') as z:
  assert z.namelist()==['enwik9'];assert z.getinfo('enwik9').file_size==1000000000
  with z.open('enwik9') as src,(W/'enwik9').open('xb') as dst:shutil.copyfileobj(src,dst,1<<20)
 assert sha(W/'enwik9')=='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'
 cmd=[str(W/'cmix'),'-e',str(W/'enwik9'),'prepared','--bytes-only','--save-ppmd-bytes',str(D/'tokens.uint8'),'--save-article-boundaries',str(D/'article_boundaries.int32')]
 with (D/'prepare.log').open('x') as log:
  p=subprocess.Popen(cmd,cwd=W,env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_'))},stdout=log,stderr=subprocess.STDOUT);m['child_pid']=p.pid;save();_,status,u=os.wait4(p.pid,0);rc=os.waitstatus_to_exitcode(status)
 assert rc==0,('bytes-only failed',rc)
 tokens=np.memmap(D/'tokens.uint8',dtype=np.uint8,mode='r');bitmap=(R/'preserved/data/vocab.bm').read_bytes();assert len(bitmap)==32
 vocab=np.array([i for i in range(256) if bitmap[i//8]>>(i%8)&1],np.uint8);assert len(vocab)==205
 target=D/'full_ready.wrt'
 with target.open('xb') as f:
  for lo in range(0,len(tokens),1<<20):
   block=np.asarray(tokens[lo:lo+(1<<20)]);assert int(block.max())<len(vocab);f.write(vocab[block].tobytes())
 m.update(full_ready={'bytes':target.stat().st_size,'sha256':sha(target)},cpu_user_seconds=u.ru_utime,max_rss_kbytes=u.ru_maxrss)
 data=target.read_bytes();m['old_slice_offsets']={}
 for n in 'abcd':
  p=R/'preserved/slices'/(n+'2m.bin') if n in 'ab' else R/(n+'2m.bin');s=p.read_bytes();at=data.find(s[:65536]);m['old_slice_offsets'][n]={'offset':at,'full2m_identical':at>=0 and data[at:at+len(s)]==s}
 m['dictionary_sha256']=sha(W/'.dict');m['reference_dictionary_match']=m['dictionary_sha256']==sha(R/'preserved/gen/.dict');assert m['reference_dictionary_match'];assert all(x['full2m_identical'] for x in m['old_slice_offsets'].values()),'Token vocabulary/order mismatch'
 m['fresh_regions']={n:{'offset':off,'bytes':2000000} for n,off in [('e',220000000),('f',480000000)]}
 for n,x in m['fresh_regions'].items():
  assert x['offset']+x['bytes']<=len(data);p=D/(n+'2m.bin');p.write_bytes(data[x['offset']:x['offset']+x['bytes']]);x['sha256']=sha(p)
 m.update(status='COMPLETE_PREPARATION_ONLY',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),training_priors='NOT_REGENERATED',raw_full_decode='NOT_VERIFIED');save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
