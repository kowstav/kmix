import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'continuous_strength_v1'
if D.exists():print(json.dumps({'reused':True,'manifest':json.loads((D/'manifest.json').read_text())}))
else:
 with (R/'continuous_strength_v1_controller.log').open('x') as log:p=subprocess.Popen(['python',str(R/'research_round8_continuous_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps({'launched':True,'pid':p.pid,'path':str(D)}))
