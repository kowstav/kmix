from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');assert not (W/'native_dispatch_v3.json').exists()
p=subprocess.Popen(['python3','/kaggle/working/research_round14_dispatch_native_worker.py'],stdout=(W/'native_dispatch_worker.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'action':'preflight_gated_four_native_CPU_commits'}))
