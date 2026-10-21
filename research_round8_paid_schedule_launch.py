import json,pathlib,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'paid_schedule_v1'
if D.exists():print(json.dumps({'launched':False,'reason':'EXISTING_JOB_OR_EVIDENCE'}))
else:
    with (R/'paid_schedule_v1_controller.log').open('x') as f:p=subprocess.Popen(['python','-u',str(R/'research_round8_paid_schedule_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'launched':True,'pid':p.pid}))
