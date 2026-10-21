import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');out={}
for n in ['native_hidden_trace_v4','hidden_cache_v2']:
 p=R/n/'manifest.json';m=json.loads(p.read_text());out[n]={'status':m['status'],'stage':m.get('stage'),'error':m.get('error'),'controls':len(m.get('controls',[])),'exports':len(m.get('exports',[])),'finished':m.get('finished'),'results':[{'name':v['name'],'dev':v['development_q16_saving_bytes'],'confirmation':v['confirmation_q16_saving_bytes'],'gap':v['supporting_plane_gap_bytes'],'coefficients':v['coefficients']} for v in m.get('results',[])]}
out['controller']=json.loads((R/'hidden_cache_v3_controller_status.json').read_text())
print(json.dumps(out))
