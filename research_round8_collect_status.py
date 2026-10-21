import json,pathlib,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');out={}
for name in ['conditional_gate_v1','weight_partition_v1','paid_schedule_v1','clean_title_v1','clean_title_v2','clean_title_v3']:
    p=R/name/'manifest.json'
    if not p.exists():out[name]={'status':'NOT_STARTED'};continue
    m=json.loads(p.read_text());s={k:v for k,v in m.items() if k not in ['sources','results']}
    if 'results' in m:
        s['results']=[]
        for r in m['results']:
            a={'slice':r['slice'],'cpu_user_seconds':r['accounting']['user_seconds'],'peak_rss_kbytes':r['accounting']['max_rss_kbytes']}
            if 'arms' in r:a['arms']=[{k:x[k] for k in ['name','saving_bytes','q16_tax_bytes','tree_nodes']} for x in r['arms']]
            if 'programs' in r:a['programs']=[{k:x[k] for k in ['name','options','saving_bytes_including_mode','mode']}|{'segments':len(x['segments'])} for x in r['programs']]
            s['results'].append(a)
    out[name]=s
out['active_processes']=subprocess.run(['ps','-eo','pid,etime,args'],capture_output=True,text=True).stdout
out['active_processes']=[line for line in out['active_processes'].splitlines() if 'round8' in line or 'conditional_gate_v1/replay' in line]
print(json.dumps(out))
