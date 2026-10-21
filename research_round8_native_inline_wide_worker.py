import datetime,hashlib,importlib.util,json,os,pathlib,shutil,subprocess,sys,time,traceback
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7')
N=R/'atom_cache_v1';S=R/'native_stage_trace_v1';A=R/'native_inline_residual_v1';W=R/'source_wide_confirmation_v1'
D=R/'native_inline_wide_v1';D.mkdir(exist_ok=False);T=D/'tree'
m={'status':'RUNNING','session':355735431,'pid':os.getpid(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'core_retraining':False,'paid_spending_usd':0,'deletions':[],'controls':[],'candidates':[],'scope':'actual frozen wider inline source coding and independent decode on cold E/F; full package qualification open','full_qualifying_archive':False}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def save(s):
 m['stage']=s;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(s,flush=True)
def run(cmd,cwd,env,label):
 t=time.monotonic()
 with (D/(label+'.log')).open('x') as f:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,s,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(s)
 a={'wall_seconds':time.monotonic()-t,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 if p.returncode:m['failed_runtime']=a;raise RuntimeError(label)
 return a
def patch(path,old,new):
 text=path.read_text();assert text.count(old)==1,(path.name,old);path.write_text(text.replace(old,new))
try:
 wm=json.loads((W/'manifest.json').read_text());am=json.loads((A/'manifest.json').read_text());nm=json.loads((N/'manifest.json').read_text());sm=json.loads((S/'manifest.json').read_text())
 assert wm['status']=='COMPLETE_FRESH_WIDER_SOURCE_EF_Q16_CONFIRMATION' and wm['wider_both_slices_improve'] and wm['wider_both_slices_beat_generic']
 assert am['status']=='COMPLETE_NATIVE_INLINE_RESIDUAL_COLD_CODING_DECODE'
 coefficients=[.0016181118716570748,-.007454085408717222,2.3818512619982752]
 assert wm['frozen_wider_coefficients']==coefficients and sha(A/'tree/cmix')==am['binary']['sha256']
 m['free_disk_bytes_before']=shutil.disk_usage(D).free;assert m['free_disk_bytes_before']>700000000
 shutil.copytree(A/'tree',T,symlinks=True,ignore=shutil.ignore_patterns('task_bin','*.o','cmix','cmix_hidden_trace'))
 m.update(frozen_coefficients=coefficients,parent_manifest_sha256=sha(A/'manifest.json'),confirmation_manifest_sha256=sha(W/'manifest.json'),production_stream=nm['production_stream'])
 files=[T/'src/predictor.h',T/'src/predictor.cpp',T/'src/coder/encoder.cpp',T/'src/coder/decoder.cpp'];m['parent_interfaces_sha256']={str(p.relative_to(T)):sha(p) for p in files}
 pred=T/'src/predictor.cpp'
 patch(pred,'  const double dot = 0.0015585303798630623 +\n      (-0.008865910048333772)*ell + double(feature);','  const double dot = 0.0016181118716570748 +\n      (-0.007454085408717222)*ell + 2.3818512619982752 * double(feature);')
 m['patched_interfaces_sha256']={str(p.relative_to(T)):sha(p) for p in files};m['source_hashes']=[{'file':v,'sha256':sha(R/v)} for v in ['research_round8_native_inline_wide_worker.py','research_round8_native_inline_wide_protocol.md']];save('isolated frozen wider coefficients installed')
 sys.path.insert(0,str(P));spec=importlib.util.spec_from_file_location('hp_original_native_helper',R/'research_round8_native_hidden_trace_worker.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.DEST=D;helper.TREE=T;compiler_path=helper.restore_compiler()
 env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','FX_PREPARE','HP_LEX_'))};env['PATH']=compiler_path;m['compiler']=sm['compiler'];m['classical_flags']=helper.FLAGS;m['transformer_flags']=helper.TF
 m['compile_accounting']=run(['make','-B','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+helper.FLAGS,'CFLAGS_TF_DEFINES='+helper.TF],T,env,'compile');binary=T/'cmix'
 m['binary']={'bytes':binary.stat().st_size,'sha256':sha(binary),'matched_observer_binary_bytes':(S/'tree/cmix').stat().st_size,'lab_binary_delta_bytes':binary.stat().st_size-(S/'tree/cmix').stat().st_size};m['coefficients_embedded_in_binary']=True;m['not_submitted_binary_delta']=True
 weights=P/'lex_audit/lex_h1_run11.tfwc2';dictionary=T/'dictionary/english.dic';assert sha(weights)==nm['weights_sha256'] and sha(dictionary)==nm['dictionary_sha256']
 base={**env,'LAB_RAW':'1','LAB_VOCAB':str(P/'preserved/data/vocab.bm'),'LAB_DICT':str(dictionary),'LAB_KEEP_TEMP':'1'}
 def evaluate(s,zero):
  label=s+('32k_zero' if zero else '512k_candidate');dest=D/label;dest.mkdir();(dest/'.dict').symlink_to(dictionary)
  ref=N/(s+'32k_hidden') if zero else W/(s+'512k');raw=N/(s+'32k.bin') if zero else ref/'input.bin';out=dest/'out.cmx';qp=dest/'final_p.u16';hidden=dest/'hidden.q8';extra={'LAB_FINAL_RESIDUAL_ZERO':'1'} if zero else {}
  save('native encode '+label);ea=run([str(binary),'-n','--transformer',str(weights),str(raw),str(out)],dest,{**base,**extra,'LAB_BITTRACE':str(qp),'LAB_HIDDENTRACE':str(hidden)},label+'_encode')
  row={'slice':s,'input_bytes':raw.stat().st_size,'archive_bytes':out.stat().st_size,'archive_sha256':sha(out),'candidate_p_sha256':sha(qp),'candidate_hidden_sha256':sha(hidden),'encode_accounting':ea,'input_sha256':sha(raw)}
  if zero:
   assert out.read_bytes()==(ref/'out.cmx').read_bytes() and qp.read_bytes()==(ref/'final_p.u16').read_bytes();row.update(native_archive_identity=True,native_Q16_identity=True)
  else:
   n=next(v for v in wm['exports'] if v['slice']==s);expected=next(v for v in wm['evaluations'] if v['slice']==s)['results'][0]
   assert row['input_sha256']==n['input_sha256'] and row['candidate_p_sha256']==expected['prediction_sha256'];assert sha(ref/'hidden.q8')==n['hidden_sha256']==row['candidate_hidden_sha256'];row.update(exact_frozen_replay_Q16_identity=True,core_hidden_state_identity=True,native_reference_archive_bytes=(ref/'out.cmx').stat().st_size,actual_archive_saving_bytes=(ref/'out.cmx').stat().st_size-out.stat().st_size,expected_Q16_likelihood_saving_bytes=expected['Q16_saving_bytes'])
  decode=D/(label+'_decode');decode.mkdir();(decode/'.dict').symlink_to(dictionary);dh=decode/'hidden.q8';dq=decode/'final_p.u16';save('independent native decode '+label)
  da=run([str(binary),'-d','--transformer',str(weights),str(out),'decoded.bin'],decode,{**base,**extra,'LAB_HIDDENTRACE':str(dh),'LAB_DECODE_BITTRACE':str(dq)},label+'_decode');assert (decode/'decoded.bin').read_bytes()==raw.read_bytes() and sha(dh)==sha(hidden) and sha(dq)==sha(qp)
  row.update(independent_decode_exact=True,encode_decode_integer_trace_identical=True,encode_decode_hidden_trace_identical=True,decode_accounting=da);(m['controls'] if zero else m['candidates']).append(row);save('native wider gates PASS '+label)
 for s in 'ab':evaluate(s,True)
 for s in 'ef':evaluate(s,False)
 m.update(actual_EF_archive_saving_bytes=sum(v['actual_archive_saving_bytes'] for v in m['candidates']),production_package_delta_measured=False,full_warm_archive_evaluated=False,free_disk_bytes_after=shutil.disk_usage(D).free,status='COMPLETE_NATIVE_INLINE_WIDE_COLD_CODING_DECODE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('actual wider cold archives and independent decodes complete; full package qualification open')
except BaseException as e:
 m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved before any named repair');raise
