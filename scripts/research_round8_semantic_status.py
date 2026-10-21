import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');out={}
for name in ['semantic_graph_v1','semantic_replay_v1']:
 p=R/name/'manifest.json'
 if p.exists():out[name]=json.loads(p.read_text())
 else:out[name]={'status':'NOT_STARTED'}
out['active_processes']=[x for x in subprocess.run(['ps','-eo','pid,etime,args'],capture_output=True,text=True).stdout.splitlines() if 'round8' in x]
print(json.dumps(out))
