import json,pathlib,subprocess
r=pathlib.Path('/kaggle/working/hp_round7');assert not (r/'root_eof_v3').exists();log=(r/'root_eof_v3_controller.log').open('x');p=subprocess.Popen(['python',str(r/'research_round7_p02_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'p02_pid':p.pid,'prior_outputs_preserved':True}))
