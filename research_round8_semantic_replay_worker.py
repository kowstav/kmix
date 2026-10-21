import datetime,hashlib,json,os,pathlib,subprocess,time,traceback
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');D=R/'semantic_replay_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'session':355655943,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':[],'deletions':[],'paid_rental_usd':0,'core_retraining':False,'scope':'Frozen pretrained semantic graph, no core retraining; paired shuffled/spelling controls; graph cost still required'}
def save(): (D/'manifest.json').write_text(json.dumps(m,indent=2))
def run(cmd,log):
    with log.open('x') as f:
        start=time.monotonic();p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);pid,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
    if p.returncode:raise RuntimeError((cmd,p.returncode,str(log)))
    return {'wall_seconds_controller':time.monotonic()-start,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss}
save()
try:
    binary=D/'replay';m['compile']=run(['g++','-O3','-std=c++17',str(R/'research_round8_semantic_replay.cpp'),'-o',str(binary)],D/'compile.log')
    m['binary']={'bytes':binary.stat().st_size,'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()};m['sources']=[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [R/'research_round8_semantic_replay.cpp',R/'research_round8_clean_library.h',R/'research_round8_observer_separated.h',R/'research_round8_semantic_protocol.md']];save()
    m['graph']=json.loads((R/'semantic_graph_v1/manifest.json').read_text())['graph'];save()
    args=[str(P/'preserved/gen/.dict'),str(P/'research_round7_remaining_graph.txt'),str(P/'research_round7_remaining_constructors.txt'),str(R/'semantic_graph_v1/semantic_k8.u16')]
    run([str(binary),'selftest',*args],D/'selftest.log');m['selftest']=[json.loads(line) for line in (D/'selftest.log').read_text().splitlines()];save()
    def evaluate(s,limit):
        tag=s+('_128k' if limit else '_2m');raw=P/'preserved/slices'/(s+'2m.bin') if s in 'ab' else P/(s+'2m.bin');trace=P/'lex_finalbit_2m_v1'/s/'final_p.u16'
        acct=run([str(binary),str(raw),str(trace),*args,str(limit),str(D/(tag+'.json'))],D/(tag+'.log'));row=json.loads((D/(tag+'.json')).read_text());row.update(accounting=acct,slice=tag);(D/(tag+'.json')).write_text(json.dumps(row,indent=2));m['results'].append(row);save();print(json.dumps({'completed':tag,'arms':row['arms'],'cpu':acct['user_seconds']}),flush=True)
        return {a['name']:a['saving_bytes'] for a in row['arms']}
    pilots=[evaluate(s,131072) for s in 'ab'];pairs=[('semantic_last_content','shuffled_last_content'),('semantic_topic_context','shuffled_topic_context')]
    passing=[]
    for target,random in pairs:
        increments=[p[target]-max(p['generic'],p[random],p['spelling_last_content']) for p in pilots]
        if min(increments)>0 and sum(increments)>=64:passing.append({'target':target,'increments_over_both_controls':increments})
    m['pilot_gate']={'threshold_bytes':64,'combined_bytes':262144,'requires_positive_each_slice':True,'passing':passing};save()
    if passing:
        for s in 'abcd':evaluate(s,0)
        m['status']='COMPLETE_CONFIRMATION_REPLAY'
    else:m['status']='COMPLETE_PILOT_NO_PROMOTION'
    m['finished']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
