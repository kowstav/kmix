from pathlib import Path
import json,os,subprocess
W=Path('/kaggle/working/hp_round13');target=W/'pulls'/'hutter-r13-native-final-head-v1';target.mkdir(exist_ok=False)
r=subprocess.run(['kaggle','kernels','output','chaoscpp/hutter-r13-native-final-head-v1','-p',str(target)],capture_output=True,text=True,timeout=40)
out={'exit':r.returncode,'files':{}}
for p in target.rglob('*'):
    if p.is_file() and p.suffix in ('.json','.log'):out['files'][str(p.relative_to(target))]=p.read_text(errors='replace')[-7000:]
(W/'native_failure_preserved_v1.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
