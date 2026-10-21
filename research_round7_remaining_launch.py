import json,pathlib,subprocess
r=pathlib.Path('/kaggle/working/hp_round7');d=r/'remaining_experts_v1'
assert not d.exists(),'Reuse existing experiment; do not relaunch'
log=(r/'remaining_experts_v1_controller.log').open('x')
p=subprocess.Popen(['python',str(r/'research_round7_remaining_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'launched_pid':p.pid,'output':str(d),'neural_training':False,'paid_rental':0,'deletions':[]}))
