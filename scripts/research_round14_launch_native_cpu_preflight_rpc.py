from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');assert not (W/'native_cpu_preflight_v1').exists()
p=subprocess.Popen(['python3','/kaggle/working/research_round14_native_cpu_preflight_worker.py'],stdout=(W/'native_cpu_preflight_worker.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'action':'six_native_preflight_cases_four_CPU_lanes'}))
