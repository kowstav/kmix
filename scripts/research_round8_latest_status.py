import json,pathlib,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');out={}
for name in ['clean_title_v4','warm_source_v1']:
    p=R/name/'manifest.json'
    if not p.exists():out[name]={'status':'NOT_STARTED'};continue
    m=json.loads(p.read_text());s={k:v for k,v in m.items() if k not in ['sources','results']}
    results=m.get('results',[])
    if isinstance(results,dict):results=list(results.values())
    s['results']=results
    out[name]=s
out['processes']=[x for x in subprocess.run(['ps','-eo','pid,etime,args'],capture_output=True,text=True).stdout.splitlines() if 'round8' in x]
print(json.dumps(out))
