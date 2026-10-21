import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');o={}
for n in ['metric_cache_v1','native_metric_fresh_v1']:
 p=R/n/'manifest.json';m=json.loads(p.read_text()) if p.exists() else {};o[n]={k:m.get(k) for k in ['status','error','pid','AB_selected_name','AB_selected_after_parameters_and_selector_bytes','fresh_advance_gate_passed','fresh_GH_evaluated']};o[n]['results_count']=len(m.get('results',[]));o[n]['exports_count']=len(m.get('exports',[]));o[n]['controller_tail']=(R/(n+'_controller.log')).read_text(errors='replace')[-500:]
o['active']=[s for s in subprocess.run(['ps','-eo','pid,etime,args'],capture_output=True,text=True).stdout.splitlines() if ('metric_cache' in s or 'metric_fresh' in s or 'native_metric_fresh' in s) and 'jupyter' not in s]
print(json.dumps(o))
