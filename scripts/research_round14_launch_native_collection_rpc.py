from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');p=W/'native_wave_collection_v1.json'
if p.exists():print(p.read_text())
else:
    q=subprocess.Popen(['python3','/kaggle/working/research_round14_collect_native_wave_worker.py'],stdout=(W/'native_wave_collection_v1.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'pid':q.pid,'manifest':str(p)}))
