import datetime,json,pathlib,subprocess,time,os
R=pathlib.Path('/kaggle/working/hp_round8');S=R/'hidden_cache_v3_controller_status.json';D=R/'hidden_cache_v2'
assert not S.exists() and not D.exists(),'Reuse existing controller/results'
m={'pid':os.getpid(),'status':'WAITING_NATIVE_IDENTITY','started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deletions':[]}
def save():S.write_text(json.dumps(m,indent=2))
save();last=None
while True:
 native=json.loads((R/'native_hidden_trace_v4/manifest.json').read_text());status=native['status']
 if status!=last:m['native_stage']=native.get('stage');save();last=status
 if status=='FAIL':m.update(status='DEPENDENCY_FAILED',error=native.get('error'));save();raise RuntimeError('Native identity prerequisite failed; no cache launch')
 if status=='COMPLETE_NATIVE_HIDDEN_IDENTITY_AND_EXPORTS':break
 time.sleep(30)
assert not D.exists();m['status']='CACHE_REPLAY_AND_FIT_RUNNING';save();p=subprocess.Popen(['python','-u',str(R/'research_round8_hidden_cache_v2_fit_worker.py')]);m['child_pid']=p.pid;save();start=time.monotonic();_,status,u=os.wait4(p.pid,0);code=os.waitstatus_to_exitcode(status);p.returncode=code
m.update(status='COMPLETE' if code==0 else 'FAILED',returncode=code,total_child_accounting={'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'wall_seconds':time.monotonic()-start},finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
if code:raise RuntimeError('Cache experiment failed; evidence retained')
