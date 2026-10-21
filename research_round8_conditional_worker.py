import datetime, hashlib, json, os, pathlib, subprocess, time, traceback
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');D=R/'conditional_gate_v1'
D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'session':355655943,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':[],'deletions':[],'paid_rental_usd':0,'core_retraining':False,'baseline':'C3 final uint16 native, cold old-FX2 slices'}
def save(): (D/'manifest.json').write_text(json.dumps(m,indent=2))
def run_process(cmd,logfile):
    with logfile.open('x') as log:
        t=time.monotonic();p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);pid,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
    if p.returncode: raise RuntimeError({'cmd':cmd,'exit':p.returncode,'log':str(logfile)})
    return {'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'wall_seconds_controller':time.monotonic()-t}
save()
try:
    binary=D/'replay'
    m['compile']=run_process(['g++','-O3','-std=c++17','-Wall','-Wextra',str(R/'research_round8_conditional.cpp'),'-o',str(binary)],D/'compile.log')
    m['binary']={'bytes':binary.stat().st_size,'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}
    m['sources']=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [R/'research_round8_conditional.cpp',R/'research_round7_remaining_experts.cpp',R/'research_round8_conditional_selftest.py',R/'research_round8_conditional_protocol.md']]
    save()
    run_process(['python',str(R/'research_round8_conditional_selftest.py'),str(binary),str(D/'selftest.json')],D/'selftest.log')
    m['selftest']=json.loads((D/'selftest.json').read_text());save()
    # All arms and the sequence are registered before result inspection.
    for slice_name,limit in [('a',32768),('b',32768),*[(s,0) for s in 'abcd']]:
        tag=slice_name+('_32k' if limit else '_2m')
        raw=P/'preserved/slices'/(slice_name+'2m.bin') if slice_name in 'ab' else P/(slice_name+'2m.bin')
        trace=P/'lex_finalbit_2m_v1'/slice_name/'final_p.u16'
        cmd=[str(binary),str(raw),str(trace),str(P/'preserved/gen/.dict'),str(P/'research_round7_remaining_graph.txt'),str(P/'research_round7_remaining_constructors.txt'),str(limit),str(D/(tag+'.json'))]
        accounting=run_process(cmd,D/(tag+'.log'));row=json.loads((D/(tag+'.json')).read_text());row.update(accounting=accounting,slice=tag)
        (D/(tag+'.json')).write_text(json.dumps(row,indent=2));m['results'].append(row);save()
        print(json.dumps({'completed':tag,'arms':[{k:a[k] for k in ['name','saving_bytes','q16_tax_bytes','tree_nodes']} for a in row['arms']],'cpu':accounting['user_seconds']}),flush=True)
    m.update(status='COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except BaseException as e:
    m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
