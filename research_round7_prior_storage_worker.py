import datetime,hashlib,json,lzma,os,pathlib,subprocess,time,traceback,zlib
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round7');D=R/'exact_prior_storage_v1';assert not D.exists();D.mkdir();m={'status':'RUNNING','pid':os.getpid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'exact native PPMD float16 block-storage feasibility, early262144WRT bytes only; not full priors or GPU parity','deletions':[],'paid_rental_usd':0}
def save():(D/'manifest.json').write_text(json.dumps(m,indent=2))
save()
try:
 binary=D/'cmix';binary.write_bytes((R/'lex_finalbit_trace_v1/cmix_trace').read_bytes());binary.chmod(0o755);inp=D/'prefix.wrt';inp.write_bytes((R/'full_stream_regen_v2/full_ready.wrt').open('rb').read(262144));(D/'.dict').symlink_to(R/'preserved/gen/.dict')
 env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};env.update(LAB_RAW='1',LAB_VOCAB=str(R/'preserved/data/vocab.bm'),LAB_KEEP_TEMP='1');prior=D/'priors.f16'
 with (D/'native.log').open('x') as log:
  p=subprocess.Popen([str(binary),'-n',str(inp),'out.cmx','--ppmd-only','--save-ppmd-probs',str(prior)],cwd=D,env=env,stdout=log,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);assert os.waitstatus_to_exitcode(status)==0
 assert prior.stat().st_size==262144*205*2;rows=[];a=np.memmap(prior,dtype='<f2',mode='r',shape=(262144,205));assert np.isfinite(a).all()
 for lo in range(0,len(a),65536):
  block=np.asarray(a[lo:lo+65536]).tobytes();record={'start':lo,'rows':65536,'raw_bytes':len(block),'sha256':hashlib.sha256(block).hexdigest(),'codecs':{}}
  for name,enc,dec in [('zlib3',lambda b:zlib.compress(b,3),zlib.decompress),('zlib9',lambda b:zlib.compress(b,9),zlib.decompress),('lzma3',lambda b:lzma.compress(b,preset=3),lzma.decompress)]:
   begin=time.monotonic();b=enc(block);ct=time.monotonic()-begin;begin=time.monotonic();back=dec(b);dt=time.monotonic()-begin;assert back==block;record['codecs'][name]={'compressed_bytes':len(b),'ratio':len(b)/len(block),'compress_seconds':ct,'decompress_seconds':dt,'exact_roundtrip':True}
  rows.append(record)
 m.update(status='COMPLETE',native_user_seconds=u.ru_utime,native_max_rss_kbytes=u.ru_maxrss,rows=262144,prior_bytes=prior.stat().st_size,prior_sha256=hashlib.sha256(prior.read_bytes()).hexdigest(),zero_fraction=float(np.mean(a==0)),blocks=rows,
  projected_full_bytes_not_guaranteed={name:240448198200*sum(x['codecs'][name]['compressed_bytes'] for x in rows)/sum(x['raw_bytes'] for x in rows) for name in ['zlib3','zlib9','lzma3']});save();print(json.dumps(m))
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
