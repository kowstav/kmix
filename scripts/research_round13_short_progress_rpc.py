from pathlib import Path
import json,subprocess,time
W=Path('/kaggle/working/hp_round13')
out={'observed_at':time.time()}
for name in ('asset_prepare_manifest.json','preflight_v1.json','dispatch_v1.json'):
    p=W/name
    if p.exists():
        value=json.loads(p.read_text());out[name]={k:value.get(k) for k in ('status','pid','asset_bytes','dataset','error','finished','jobs')}
out['processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,comm','--sort=-%cpu'],text=True).splitlines()[:10]
print(json.dumps(out))
