import pathlib,json,subprocess,shutil
R=pathlib.Path('/kaggle/working/hp_round8');rows=[]
for name in ['atom_cache_v1','error_memory_v1']:
 d=R/name;p=d/'manifest.json';m=json.loads(p.read_text()) if p.exists() else {};tail=[]
 for log in sorted(d.glob('*.log'),key=lambda p:p.stat().st_mtime,reverse=True)[:2]:tail.append({'name':log.name,'tail':log.read_text(errors='replace')[-900:]})
 rows.append({'experiment':name,'status':m.get('status'),'stage':m.get('stage'),'pid':m.get('pid'),'error':m.get('error'),'controls_complete':len(m.get('controls',[])),'native_exports_complete':len(m.get('native_exports',[])),'feature_exports_complete':len(m.get('feature_exports',[])),'heads_complete':len(m.get('results',[])),'latest_logs':tail})
ps=subprocess.check_output(['ps','-eo','pid,comm,etime,pcpu,rss,args'],text=True)
selected=[s for s in ps.splitlines() if '/cmix_hidden_trace ' in s or '/reference_cmix ' in s or '/error_memory_v1/replay ' in s or '/atom_cache_v1/replay ' in s]
print(json.dumps({'jobs':rows,'active_native_processes':selected,'working_free_bytes':shutil.disk_usage(R).free}))
