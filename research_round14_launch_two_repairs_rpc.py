from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');out=[]
for name,guard in [('research_round14_restore_compiler_worker.py','compiler_restore_v1.json'),('research_round14_ppmd_diagnose_worker.py','ppmd_diagnostic_v1.json')]:
    assert not (W/guard).exists()
    p=subprocess.Popen(['python3','/kaggle/working/'+name],stdout=(W/(name+'.log')).open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
    out.append({'worker':name,'pid':p.pid})
print(json.dumps(out))
