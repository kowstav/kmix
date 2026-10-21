from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');assert not (W/'native_cpu_build_v1.json').exists()
p=subprocess.Popen(['python3','/kaggle/working/research_round14_build_native_cpu_worker.py'],stdout=(W/'native_cpu_build_worker.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'action':'build_five_frozen_controlled_binaries'}))
