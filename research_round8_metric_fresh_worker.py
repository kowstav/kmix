import datetime,hashlib,json,os,pathlib,subprocess,time,traceback
P=pathlib.Path('/kaggle/working/hp_round7');R=pathlib.Path('/kaggle/working/hp_round8');D=R/'native_metric_fresh_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registered_offsets':{'g':310000000,'h':520000000},'length':131072,'core_retraining':False,'paid_rental_usd':0,'deletions':[],'scope':'fresh cold-native baselines; no candidate labels evaluated','exports':[]}
def save():(D/'manifest.json').write_text(json.dumps(m,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd,cwd,env,tag):
 t=time.monotonic()
 with (D/(tag+'.log')).open('x') as f:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 a={'wall_seconds':time.monotonic()-t,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 if p.returncode:raise RuntimeError((tag,p.returncode))
 return a
save()
try:
 source=P/'full_stream_regen_v2/full_ready.wrt';assert source.stat().st_size==586459020;binary=R/'native_hidden_trace_v1/cmix_hidden_trace';weights=P/'lex_audit/lex_h1_run11.tfwc2';m['binary_sha256']=sha(binary);m['weights_sha256']=sha(weights)
 base={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};base.update(LAB_RAW='1',LAB_VOCAB=str(P/'preserved/data/vocab.bm'),LAB_DICT=str(P/'preserved/gen/.dict'),LAB_KEEP_TEMP='1')
 for name,offset in m['registered_offsets'].items():
  with source.open('rb') as f:f.seek(offset);raw=f.read(131072)
  assert len(raw)==131072;inp=D/(name+'128k.bin');inp.write_bytes(raw);d=D/(name+'_128k');d.mkdir();(d/'.dict').symlink_to(P/'preserved/gen/.dict');env={**base,'LAB_BITTRACE':str(d/'final_p.u16'),'LAB_HIDDENTRACE':str(d/'hidden.q8')};enc=run([str(binary),'-n','--transformer',str(weights),str(inp),'out.cmx'],d,env,name+'_encode');assert (d/'final_p.u16').stat().st_size==16*131072 and (d/'hidden.q8').stat().st_size==193*131072
  dd=D/(name+'_decode');dd.mkdir();(dd/'.dict').symlink_to(P/'preserved/gen/.dict');dec=run([str(binary),'-d','--transformer',str(weights),str(d/'out.cmx'),'decoded.bin'],dd,{**base,'LAB_HIDDENTRACE':str(dd/'hidden.q8')},name+'_decode');assert (dd/'decoded.bin').read_bytes()==raw and (dd/'hidden.q8').read_bytes()==(d/'hidden.q8').read_bytes()
  m['exports'].append({'name':name,'offset':offset,'input_sha256':sha(inp),'hidden_sha256':sha(d/'hidden.q8'),'final_p_sha256':sha(d/'final_p.u16'),'archive_sha256':sha(d/'out.cmx'),'archive_bytes':(d/'out.cmx').stat().st_size,'raw_decode_exact':True,'encode_decode_hidden_equal':True,'encode':enc,'decode':dec});save()
 m.update(status='COMPLETE_FRESH_NATIVE_BASELINES_UNEXAMINED_BY_CANDIDATE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
