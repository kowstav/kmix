import pathlib,json,subprocess,shutil
R=pathlib.Path('/kaggle/working/hp_round9');out={}
for name in ['core_bf16_qat_v1','native_promotion_v1','native_bf16_promotion_v1','core_selective_v1','word_cache_gated_v2','model_order_v3','core_pipeline_profile_v2']:
 p=R/name/'manifest.json'
 if p.exists():
  j=json.loads(p.read_text());out[name]={k:j.get(k) for k in ['status','pid','stage','error']};out[name]['rungs']=len(j.get('rungs',[]));out[name]['archives']=len(j.get('native_candidates',j.get('archives',j.get('candidates',[]))))
print(json.dumps(out));print(subprocess.check_output(['nvidia-smi','--query-gpu=index,utilization.gpu,memory.used','--format=csv,noheader'],text=True))
print(json.dumps({'working_free':shutil.disk_usage('/kaggle/working').free,'root_free':shutil.disk_usage('/root').free}))
