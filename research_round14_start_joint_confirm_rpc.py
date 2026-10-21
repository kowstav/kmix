from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14')
assert not (W/'guard_match_confirm_a_dispatch_v8.json').exists()
with (W/'guard_match_confirm_a_dispatch_v8.log').open('xb') as f:
    p=subprocess.Popen(['python3',str(W/'dispatch_guard_match_confirmation.py.dat'),'--role','a'],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'dispatcher_pid':p.pid,'role':'a','no_gpu':True}))
