import datetime,hashlib,json,os,pathlib,subprocess,time,traceback
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');D=R/'warm_source_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'session':355655943,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deletions':[],'paid_rental_usd':0,'core_retraining':False,'scope':'warm prefix statistical source, native CORE STILL COLD; not archive qualification'}
def save(): (D/'manifest.json').write_text(json.dumps(m,indent=2))
def run(cmd,log):
    with log.open('x') as f:
        start=time.monotonic();p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);pid,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
    account={'wall_seconds':time.monotonic()-start,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
    if p.returncode:m['failed_runtime']=account;save();raise RuntimeError((cmd,p.returncode,str(log)))
    return account
save()
try:
    binary=D/'replay';m['compile']=run(['g++','-O3','-std=c++17',str(R/'research_round8_warm_source.cpp'),'-o',str(binary)],D/'compile.log');m['binary']={'bytes':binary.stat().st_size,'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()};m['sources']=[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [R/'research_round8_warm_source.cpp',R/'research_round8_clean_title_library.h',R/'research_round8_clean_library.h',R/'research_round8_observer_separated.h',R/'research_round8_warm_source_protocol.md']];save()
    m['runtime']=run([str(binary),str(P/'full_stream_regen_v2/full_ready.wrt'),str(P/'preserved/gen/.dict'),str(P/'research_round7_remaining_graph.txt'),str(P/'research_round7_remaining_constructors.txt'),str(P),str(D/'results.json')],D/'replay.log');row=json.loads((D/'results.json').read_text());cold=json.loads((R/'clean_title_v4/a_128k.json').read_text());warm=row['queries'][0];assert [a['prediction_hash'] for a in cold['arms']]==[a['prediction_hash'] for a in warm['arms']], 'independent byte traversal changed cold A predictions'
    m.update(status='COMPLETE_CONDITIONAL_DIAGNOSTIC',cold_a_all_prediction_hashes_equal=True,results=row,finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
