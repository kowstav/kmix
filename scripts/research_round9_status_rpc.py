import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');m={}
for name in ['core_setup_v1','causal_sequence_v1','full_word_alignment_v1','full_word_alignment_v2','core_training_v1','core_training_v2','hidden_sequence_v1','hidden_sequence_v2','adaptive_source_v1']:
 p=R/name/'manifest.json'
 if p.exists():
  v=json.loads(p.read_text());m[name]={k:v.get(k) for k in ['status','pid','stage','error','gpu','start','started','finish','finished']};m[name]['rungs']=len(v.get('rungs',[]))
 p=R/(name+'.log')
 if p.exists():m.setdefault(name,{})['log_tail']=p.read_text()[-2000:]
m['gpu']=subprocess.check_output(['nvidia-smi','--query-gpu=index,name,memory.used,utilization.gpu','--format=csv,noheader'],text=True)
print(json.dumps(m))
