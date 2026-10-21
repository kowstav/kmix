import json,pathlib,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'clean_title_v3'
if D.exists():print(json.dumps({'launched':False,'reason':'EXISTING_JOB_OR_EVIDENCE'}))
else:
    with (R/'clean_title_v3_controller.log').open('x') as f:p=subprocess.Popen(['python','-u',str(R/'research_round8_clean_title_v3_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'launched':True,'pid':p.pid}))
