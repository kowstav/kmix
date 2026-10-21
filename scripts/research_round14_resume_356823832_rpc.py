from pathlib import Path
import json, subprocess, time, hashlib
W=Path('/kaggle/working/hp_round14')
out={'time':time.time(),'session':356823832,'deletions':[]}
collector=(W/'confirmation_collector_v1.py.dat').read_bytes()
assert hashlib.sha256(collector).hexdigest()=='ec1adc3c3c1d14cb4d5d04ddfee38fa22eb511380051db653040ab00472e1272'
Path('/root/research_round14_collect_confirmation_worker.py').write_bytes(collector)
p=W/'confirm_b_dispatch_v5.json'
if p.exists():
    out['b_existing']=json.loads(p.read_text())
else:
    script=Path('/kaggle/working/research_round14_dispatch_confirmation_worker.py')
    assert script.is_file()
    log=(W/'confirm_b_dispatch_v5.log').open('xb')
    child=subprocess.Popen(['python3',str(script),'--role','b'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    log.close();out['b_dispatch_pid']=child.pid
for key, wave in [('a','a'),('combo','combo')]:
    tag=key+'-20261009-1734'
    record=W/('confirmation_collection_'+tag+'.json')
    assert not record.exists(),'existing collection: inspect, do not duplicate'
    log=(W/('confirmation_collection_'+tag+'.log')).open('xb')
    child=subprocess.Popen(['python3','/root/research_round14_collect_confirmation_worker.py','--wave',wave,'--tag',tag],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    log.close();out['collector_'+key+'_pid']=child.pid
(W/'resume_356823832_v1.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
