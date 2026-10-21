from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');out=[]
for name,guard in [('research_round14_rebuild_native_cpu_v2.py','native_cpu_build_v2.json'),('research_round14_ppmd_real_diagnostic_worker.py','ppmd_real_diagnostic_v1.json')]:
    assert not (W/guard).exists();p=subprocess.Popen(['python3','/kaggle/working/'+name],stdout=(W/(name+'.log')).open('ab'),stderr=subprocess.STDOUT,start_new_session=True);out.append({'worker':name,'pid':p.pid})
print(json.dumps(out))
