import pathlib,json,subprocess,shutil
R=pathlib.Path('/kaggle/working/hp_round8');names=['conditional_gate_v1','weight_partition_v1','paid_schedule_v1','clean_title_v4','warm_source_v1','semantic_graph_v1','semantic_replay_v1','continuous_strength_v2','fixed_semantic_v1','directed_memory_v1'];out={}
for name in names:
 p=R/name/'manifest.json'
 if p.exists():
  m=json.loads(p.read_text());out[name]={'status':m['status'],'pid':m.get('pid'),'finished':m.get('finished'),'results_count':len(m.get('results',[])),'error':m.get('error')}
 else:out[name]={'status':'MISSING_MANIFEST'}
out['active_processes']=[x for x in subprocess.run(['ps','-eo','pid,etime,args'],capture_output=True,text=True).stdout.splitlines() if 'round8' in x]
out['free_working_bytes']=shutil.disk_usage('/kaggle/working').free
print(json.dumps(out))
