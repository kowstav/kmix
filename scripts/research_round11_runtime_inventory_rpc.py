from pathlib import Path
import json
import shutil
import subprocess
import os
import time

out={'time':time.time(),'tools':{n:shutil.which(n) for n in ['clang++-17','clang++','g++','make','kaggle']},
     'retained_tree_makefile':Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree/makefile').exists()}
for name in ['weight_codec_v1/manifest.json','warm_atlas_v2/manifest.json']:
    p=Path('/kaggle/working/hp_round11')/name
    if p.exists():
        r=json.loads(p.read_text()); out[name]={k:r.get(k) for k in ['status','pid','child_pid','stage','error','cases','neutral_original_byte_identity']}
result=subprocess.run(['kaggle','kernels','list','--mine','--search','integer','--csv'],capture_output=True,text=True,timeout=15)
raw=result.stdout
for key in ['KAGGLE_API_TOKEN','KAGGLE_KEY']:
    if os.environ.get(key): raw=raw.replace(os.environ[key],'[CREDENTIAL REDACTED]')
out['integer_owner_inventory']={'exit':result.returncode,'stdout':raw[:5000]}
out['processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,time,%cpu,%mem,comm','--sort=-%cpu'],text=True).splitlines()[:10]
print(json.dumps(out))
