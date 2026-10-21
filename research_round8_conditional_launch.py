import json, os, pathlib, subprocess
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'conditional_gate_v1'
if D.exists():
    print(json.dumps({'launched':False,'reason':'EXISTING_JOB_OR_EVIDENCE','manifest':json.loads((D/'manifest.json').read_text()) if (D/'manifest.json').exists() else None}))
else:
    with (R/'conditional_gate_v1_controller.log').open('x') as f:
        p=subprocess.Popen(['python','-u',str(R/'research_round8_conditional_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'launched':True,'pid':p.pid,'log':str(R/'conditional_gate_v1_controller.log')}))
