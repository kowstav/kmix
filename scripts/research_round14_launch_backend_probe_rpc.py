from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');assert not (W/'ppmd_backend_probe_v2.json').exists()
p=subprocess.Popen(['python3','/kaggle/working/research_round14_ppmd_backend_probe_worker.py'],stdout=(W/'ppmd_backend_probe_v2.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'action':'backend_diagnostic_only_no_quality_selection'}))
