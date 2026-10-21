import datetime,hashlib,json,os,pathlib,subprocess,time,traceback
import numpy as np
P=pathlib.Path('/kaggle/working/hp_round7');R=pathlib.Path('/kaggle/working/hp_round8');OLD=R/'native_hidden_trace_v1';D=R/'native_hidden_trace_v2';D.mkdir(exist_ok=False)
old=json.loads((OLD/'manifest.json').read_text());assert old['status']=='FAIL' and old['error']=="FileNotFoundError(2, 'No such file or directory')"
binary=OLD/'cmix_hidden_trace';assert hashlib.sha256(binary.read_bytes()).hexdigest()==old['binary']['sha256']
m={**{k:v for k,v in old.items() if k not in ['status','stage','pid','started','error','traceback','controls','exports']},'status':'RUNNING','pid':os.getpid(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prior_failure':'native_hidden_trace_v1: missing /usr/bin/time; preserved','reused_binary_and_build':True,'controls':[],'exports':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps({'status':m['status'],'stage':stage}),flush=True)
def run(cmd,cwd,env,label):
 start=time.monotonic()
 with (D/(label+'.log')).open('x') as f:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 account={'wall_seconds':time.monotonic()-start,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 if p.returncode:m['failed_runtime']=account;save('native command failed');raise RuntimeError((cmd,p.returncode,label))
 return account
try:
 weights=P/'lex_audit/lex_h1_run11.tfwc2';base=P/'lex_finalbit_trace_v1/cmix_trace'
 e={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};e.update(LAB_RAW='1',LAB_VOCAB=str(P/'preserved/data/vocab.bm'),LAB_DICT=str(P/'preserved/gen/.dict'),LAB_KEEP_TEMP='1')
 save('reused observation-only native build: 32K controls')
 for s in 'ab':
  raw=(P/'preserved/slices'/(s+'2m.bin')).read_bytes()[:32768];inp=D/(s+'32k.bin');inp.write_bytes(raw);runs={}
  for mode,program in [('reference',base),('hidden',binary)]:
   d=D/(s+'_'+mode);d.mkdir();(d/'.dict').symlink_to(P/'preserved/gen/.dict');ee={**e,'LAB_BITTRACE':str(d/'final_p.u16')}
   if mode=='hidden':ee['LAB_HIDDENTRACE']=str(d/'hidden.q8')
   runs[mode]=run([str(program),'-n','--transformer',str(weights),str(inp),'out.cmx'],d,ee,s+'_'+mode)
  a,b=D/(s+'_reference'),D/(s+'_hidden');assert (a/'out.cmx').read_bytes()==(b/'out.cmx').read_bytes();assert (a/'final_p.u16').read_bytes()==(b/'final_p.u16').read_bytes()==(P/'lex_finalbit_2m_v1'/s/'final_p.u16').read_bytes()[:16*len(raw)];assert (b/'hidden.q8').stat().st_size==193*len(raw)
  d=D/(s+'_decode');d.mkdir();(d/'.dict').symlink_to(P/'preserved/gen/.dict');runs['decode']=run([str(binary),'--transformer',str(weights),str(b/'out.cmx'),'decoded.bin'],d,{**e,'LAB_HIDDENTRACE':str(d/'hidden.q8')},s+'_decode');assert (d/'decoded.bin').read_bytes()==raw;assert (d/'hidden.q8').read_bytes()==(b/'hidden.q8').read_bytes()
  m['controls'].append({'slice':s,'archive_identity':True,'integer_trace_identity':True,'raw_decode_exact':True,'hidden_encode_decode_identical':True,'hidden_bytes':193*len(raw),'hidden_sha256':sha(b/'hidden.q8'),'archive_sha256':sha(b/'out.cmx'),'accounting':runs});save('32K native identity/decode '+s+' PASS')
 m['status']='NATIVE_IDENTITY_PASS_EXPORTING';save('cold128K hidden trace export')
 for s in 'abcd':
  src=P/'preserved/slices'/(s+'2m.bin') if s in 'ab' else P/(s+'2m.bin');inp=D/(s+'128k.bin');inp.write_bytes(src.read_bytes()[:131072]);d=D/(s+'_128k');d.mkdir();(d/'.dict').symlink_to(P/'preserved/gen/.dict');ee={**e,'LAB_BITTRACE':str(d/'final_p.u16'),'LAB_HIDDENTRACE':str(d/'hidden.q8')};account=run([str(binary),'-n','--transformer',str(weights),str(inp),'out.cmx'],d,ee,s+'_128k');p=(d/'final_p.u16').read_bytes();assert p==(P/'lex_finalbit_2m_v1'/s/'final_p.u16').read_bytes()[:16*131072];rows=np.fromfile(d/'hidden.q8',np.uint8).reshape(-1,193);assert len(rows)==131072 and np.all(rows[:,0]<=1)
  m['exports'].append({'slice':s,'input_bytes':131072,'input_sha256':sha(inp),'hidden_sha256':sha(d/'hidden.q8'),'hidden_valid_rows':int(rows[:,0].sum()),'final_p_sha256':sha(d/'final_p.u16'),'integer_trace_identity':True,'accounting':account});save('cold128K export '+s+' PASS')
 m.update(status='COMPLETE_NATIVE_HIDDEN_IDENTITY_AND_EXPORTS',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('ready for preregistered causal cache replay')
except BaseException as ex:m.update(status='FAIL',error=repr(ex),traceback=traceback.format_exc());save('failure preserved; no automatic duplicate launch');raise
