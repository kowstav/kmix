import pathlib,os,json,time,subprocess,hashlib,traceback
W=pathlib.Path('/kaggle/working');D=W/'hp_round10/preflight_v3';D.mkdir(exist_ok=False)
S=pathlib.Path('/root/hp_round10/preflight_v3');S.mkdir(parents=True,exist_ok=False)
T=W/'hp_round8/native_stage_trace_v1/tree';B=T/'cmix';B.chmod(B.stat().st_mode|0o100)
m={'status':'RUNNING','pid':os.getpid(),'started':time.time(),'scratch':str(S),'cases':[]}
def save():(D/'manifest.json').write_text(json.dumps(m,indent=2))
try:
 assert hashlib.sha256(B.read_bytes()).hexdigest()=='17768b0673e5a1ad6fb39ca86af25d6d40db3b1790fc17e365341456819fd3fa'
 with (W/'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt').open('rb') as f:raw=f.read(4096)
 (S/'input.bin').write_bytes(raw);(S/'.dict').symlink_to(T/'dictionary/english.dic');weights=W/'hp_round7/lex_audit/lex_h1_run11.tfwc2'
 env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};env.update(LAB_RAW='1',LAB_DICT=str(T/'dictionary/english.dic'),LAB_VOCAB=str(W/'hp_round7/preserved/data/vocab.bm'),LAB_KEEP_TEMP='1')
 save()
 for name,args in [('encode',[str(B),'-n','--transformer',str(weights),'input.bin','out.cmx']),('decode',[str(B),'-d','--transformer',str(weights),'out.cmx','decoded.bin'])]:
  start=time.monotonic()
  with (D/(name+'.log')).open('x') as f:p=subprocess.run(args,cwd=S,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
  m['cases'].append({'name':name,'exit_code':p.returncode,'wall_seconds':time.monotonic()-start});save();assert p.returncode==0,(name,p.returncode)
 assert (S/'decoded.bin').read_bytes()==raw
 m.update(status='COMPLETE_NATIVE_PREFLIGHT_PASS',input_sha256=hashlib.sha256(raw).hexdigest(),finished=time.time());save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
