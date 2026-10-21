from pathlib import Path
import subprocess,json
p=Path('/kaggle/working/hp_round14/ppmd_native_probe_v2.json')
if p.exists():print('existing',p.read_text())
else:
    f=Path('/kaggle/working/hp_round14/ppmd_native_probe_v2.log').open('ab')
    q=subprocess.Popen(['python3','/kaggle/working/research_round14_ppmd_native_probe_v2_worker.py'],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'pid':q.pid,'manifest':str(p)}))
