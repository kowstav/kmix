import datetime,hashlib,json,os,pathlib,subprocess,time,traceback
R=pathlib.Path('/kaggle/working/hp_round8');N=R/'atom_cache_v1';D=R/'role_residual_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','session':355735431,'pid':os.getpid(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'core_retraining':False,'paid_spending_usd':0,'deletions':[],'evaluations':[],'confirmation_evaluated':False,'advance_gate_bytes':64,'full_native_candidate':False}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def run(cmd,label):
 start=time.monotonic()
 with (D/(label+'.log')).open('x') as f:p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);_,s,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(s)
 a={'wall_seconds':time.monotonic()-start,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'peak_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 assert p.returncode==0,(label,a);return a
try:
 nm=json.loads((N/'manifest.json').read_text());dictionary=R/'native_hidden_trace_v1/tree/dictionary/english.dic';assert sha(dictionary)==nm['dictionary_sha256'];m['production_stream']=nm['production_stream'];m['source_hashes']=[{'file':s,'sha256':sha(R/s)} for s in ['research_round8_role_residual.cpp','research_round8_role_residual_protocol.md','research_round8_role_residual_worker.py','research_round8_atom_cache.cpp']];save('registered native-offset online role residual')
 binary=D/'replay';m['compile']=run(['g++','-O3','-march=x86-64-v3','-mrecip=none','-std=c++17',str(R/'research_round8_role_residual.cpp'),'-o',str(binary)],'compile');m['binary_sha256']=sha(binary);m['selftest_accounting']=run([str(binary),'selftest'],'selftest');m['selftest']=json.loads((D/'selftest.log').read_text())
 def export(s):
  v=next(v for v in nm['native_exports'] if v['slice']==s);raw=N/(s+'512k.bin');p=N/(s+'_native/final_p.u16');assert sha(raw)==v['input_sha256'] and sha(p)==v['final_p_sha256'];out=D/(s+'.json');args=[str(binary),str(raw),str(p),str(dictionary),str(out),'524288']
  if s=='a':args.append(str(D/'original.prefix_predictions'))
  account=run(args,s);row=json.loads(out.read_text());row.update(slice=s,accounting=account,input_sha256=v['input_sha256'],native_p_sha256=v['final_p_sha256']);m['evaluations'].append(row);save('replay '+s+' complete')
 for s in 'ab':export(s)
 raw=bytearray((N/'a512k.bin').read_bytes()[:8192]);changed=False
 for i in range(4096,8192):
  if raw[i]==32 and raw[i-1]!=12:raw[i]=10;changed=True;break
 assert changed;(D/'future.bin').write_bytes(raw);m['future_accounting']=run([str(binary),str(D/'future.bin'),str(N/'a_native/final_p.u16'),str(dictionary),str(D/'future.json'),'8192',str(D/'future.prefix_predictions')],'future');assert (D/'future.prefix_predictions').read_bytes()==(D/'original.prefix_predictions').read_bytes();m['future_target_noninterference']='PASS';m['prefix_prediction_bytes_compared']=(D/'original.prefix_predictions').stat().st_size
 totals=[sum(v['results'][j]['Q16_saving_bytes'] for v in m['evaluations']) for j in range(27)];best=max(range(27),key=lambda j:totals[j]);m['development_policy_gains_bytes']=totals;m['selected_policy']=best;m['best_development_after_5bit_selector_bytes']=totals[best]-.625;m['mixture_development_saving_bytes']=sum(v['mixture_Q16_saving_bytes'] for v in m['evaluations']);m['advance_gate_pass']=max(m['best_development_after_5bit_selector_bytes'],m['mixture_development_saving_bytes'])>=64;save('locked A/B gate')
 if m['advance_gate_pass']:
  for s in 'cd':export(s)
  m['selected_policy_confirmation_saving_bytes']=sum(v['results'][best]['Q16_saving_bytes'] for v in m['evaluations'] if v['slice'] in 'cd');m['mixture_confirmation_saving_bytes']=sum(v['mixture_Q16_saving_bytes'] for v in m['evaluations'] if v['slice'] in 'cd');m['confirmation_evaluated']=True
 m.update(status='COMPLETE_CANONICAL_ROLE_RESIDUAL_DIAGNOSTIC',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('finite branch complete; full native package remains open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
