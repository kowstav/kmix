from pathlib import Path
import json,subprocess,time
W=Path('/kaggle/working/hp_round14');out={'observed_at':time.time()}
for n in ('paginated_collection_v2.json','word_costs_v2/manifest.json'):
    p=W/n
    if p.exists():
        m=json.loads(p.read_text());out[n]={k:v for k,v in m.items() if k not in ('shards','jobs')}
        if 'jobs' in m:out[n]['jobs']=[{k:v for k,v in r.items() if k!='new_files'} for r in m['jobs']]
        out[n]['shards_completed']=len(m.get('shards',[]))
for slug in ('native-confirmation-a','article-order-ppmd'):
    p=subprocess.run(['kaggle','kernels','status','chaoscpp/hutter-r14-'+slug+'-v1'],capture_output=True,text=True,timeout=20)
    out[slug]={'exit':p.returncode,'status':(p.stdout+p.stderr)[-700:]}
print(json.dumps(out))
