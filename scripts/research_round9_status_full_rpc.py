import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');out={}
for name in ['adaptive_native_v2','word_events_v1','core_layer_gpu_v4','core_extension_v1','core_export_v1']:
 p=R/name/'manifest.json'
 if p.exists():
  j=json.loads(p.read_text());out[name]={k:j.get(k) for k in ['status','pid','stage','error','actual_GH_saving_bytes','event_counts']};out[name]['rungs']=len(j.get('rungs',[]));out[name]['candidate_count']=len(j.get('candidates',j.get('native_candidates',[])))
print(json.dumps(out));print(subprocess.check_output(['nvidia-smi','--query-gpu=index,utilization.gpu,memory.used','--format=csv,noheader'],text=True));print(json.dumps({'core_data_v1_files':[p.name for p in pathlib.Path('/root/hp_round9/core_data_v1').iterdir() if p.is_file()]}))
