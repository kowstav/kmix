import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');out={}
for name in ['adaptive_native_v2','core_layer_gpu_v3','core_extension_v1']:
 p=R/name/'manifest.json'
 if p.exists():
  j=json.loads(p.read_text());out[name]={k:j.get(k) for k in ['status','pid','stage','error','actual_GH_saving_bytes']};out[name]['rungs']=len(j.get('rungs',[]));out[name]['candidates']=j.get('candidates',[])
print(json.dumps(out));print(subprocess.check_output(['nvidia-smi','--query-gpu=index,utilization.gpu,memory.used','--format=csv,noheader'],text=True))
