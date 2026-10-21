import pathlib,subprocess,json
r=pathlib.Path('/kaggle/working/hp_round7');assert not (r/'full_inverse_v1').exists();log=(r/'full_inverse_v1_controller.log').open('x');p=subprocess.Popen(['python',str(r/'research_round7_full_inverse_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'full_inverse_pid':p.pid}))
