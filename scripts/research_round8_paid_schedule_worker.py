import datetime,hashlib,json,os,pathlib,subprocess,time,traceback
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');D=R/'paid_schedule_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'session':355655943,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':[],'deletions':[],'paid_rental_usd':0,'core_retraining':False}
def save(): (D/'manifest.json').write_text(json.dumps(m,indent=2))
def run(cmd,log):
    with log.open('x') as f:
        start=time.monotonic();p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);pid,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
    if p.returncode:raise RuntimeError((cmd,p.returncode,str(log)))
    return {'wall_seconds_controller':time.monotonic()-start,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss}
save()
try:
    binary=D/'replay';m['compile']=run(['g++','-O3','-std=c++17',str(R/'research_round8_paid_schedule.cpp'),'-o',str(binary)],D/'compile.log')
    m['binary']={'bytes':binary.stat().st_size,'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()};m['sources']=[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [R/'research_round8_paid_schedule.cpp',R/'research_round8_conditional_library.h',R/'research_round7_remaining_experts.cpp',R/'research_round8_paid_schedule_protocol.md',R/'research_round8_paid_schedule_selftest.py']];save()
    run(['python',str(R/'research_round8_paid_schedule_selftest.py'),str(binary),str(D/'selftest.json')],D/'selftest.log');m['selftest']=json.loads((D/'selftest.json').read_text());save()
    for s,limit in [('a',32768),*[(n,0) for n in 'abcd']]:
        tag=s+('_32k' if limit else '_2m');raw=P/'preserved/slices'/(s+'2m.bin') if s in 'ab' else P/(s+'2m.bin');trace=P/'lex_finalbit_2m_v1'/s/'final_p.u16'
        acct=run([str(binary),str(raw),str(trace),str(P/'preserved/gen/.dict'),str(P/'research_round7_remaining_graph.txt'),str(P/'research_round7_remaining_constructors.txt'),str(limit),str(D/(tag+'.json'))],D/(tag+'.log'))
        row=json.loads((D/(tag+'.json')).read_text());row.update(accounting=acct,slice=tag);(D/(tag+'.json')).write_text(json.dumps(row,indent=2));m['results'].append(row);save();print(json.dumps({'completed':tag,'programs':[{k:x[k] for k in ['name','saving_bytes_including_mode','mode']} for x in row['programs']],'cpu':acct['user_seconds']}),flush=True)
    m.update(status='COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
