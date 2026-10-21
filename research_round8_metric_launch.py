import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'metric_cache_v1').exists() and not (R/'native_metric_fresh_v1').exists()
out=[]
for name,worker in [('metric_cache_v1','research_round8_metric_cache_worker.py'),('native_metric_fresh_v1','research_round8_metric_fresh_worker.py')]:
 p=subprocess.Popen(['python','-u',str(R/worker)],stdout=(R/(name+'_controller.log')).open('x'),stderr=subprocess.STDOUT,start_new_session=True);out.append({'experiment':name,'pid':p.pid})
print(json.dumps({'jobs':out,'fresh_offsets_registered':[310000000,520000000],'spent_usd':0,'deletions':[]}))
