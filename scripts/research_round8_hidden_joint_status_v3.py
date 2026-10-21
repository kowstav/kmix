import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');out={}
for name in ['native_hidden_trace_v4','hidden_cache_v2']:
 p=R/name/'manifest.json'
 if p.exists():
  m=json.loads(p.read_text());out[name]={k:m.get(k) for k in ['status','stage','pid','error','results']};out[name]['controls_count']=len(m.get('controls',[]));out[name]['exports_count']=len(m.get('exports',[]))
p=R/'hidden_cache_v3_controller_status.json';out['controller']=json.loads(p.read_text()) if p.exists() else None
out['active']=[s for s in subprocess.run(['ps','-eo','pid,etime,args'],capture_output=True,text=True).stdout.splitlines() if any(k in s for k in ['native_hidden_trace','hidden_cache_v2','hidden_cache_v3_controller']) and 'jupyter' not in s]
print(json.dumps(out))
