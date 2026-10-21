import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round10');out={}
for p in R.glob('*/manifest.json'):
 j=json.loads(p.read_text());out[p.parent.name]={k:j.get(k) for k in ['status','pid','child_pid','stage','error']}
print(json.dumps(out));print(subprocess.check_output(['ps','-eo','pid,ppid,etime,time,%cpu,%mem,comm','--sort=-%cpu'],text=True).splitlines()[:7])
