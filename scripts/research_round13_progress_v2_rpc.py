from pathlib import Path
import json,subprocess,time
W=Path('/kaggle/working/hp_round13')
out={'observed_at':time.time()}
for relative in ('compiler_restore_v1.json','dispatch_v1.json'):
    p=W/relative
    if p.exists():out[relative]=json.loads(p.read_text())
fallback=Path('/kaggle/working/hp_round12_claude/warm_fallback/manifest.json')
if fallback.exists():out['fallback_manifest']=json.loads(fallback.read_text())
out['processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,psr,comm','--sort=-%cpu'],text=True).splitlines()[:16]
for name in ('llvm17_update.log','llvm17_install.log'):
    p=W/name
    if p.exists():out[name]=p.read_text(errors='replace')[-4500:]
print(json.dumps(out))
