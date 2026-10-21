import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');out={}
for name in ['core_training_v2','hidden_sequence_v2','adaptive_source_v1','adaptive_native_v1','core_layer_probe_v1','core_layer_gpu_v1','core_layer_gpu_v2','core_extension_v1']:
 p=R/name/'manifest.json'
 if p.exists():
  v=json.loads(p.read_text());out[name]={k:v.get(k) for k in ['status','pid','stage','error','finished','peak_cuda_bytes','peak_gpu_bytes']};out[name]['rungs']=len(v.get('rungs',[]));out[name]['parity']=v.get('zero_update_likelihood_parity',[])[:2]
  if v.get('error'):out[name]['traceback']=v.get('traceback','')[-2000:]
out['gpu']=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader'],text=True)
out['processes']=subprocess.check_output(['ps','-eo','pid,ppid,pcpu,etime,args'],text=True)[-2500:]
print(json.dumps(out))
