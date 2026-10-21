import json,pathlib,subprocess,sys
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'rarity_residual_pilot_v1'
if D.exists():print(json.dumps({'duplicate_not_launched':True,'manifest':json.loads((D/'manifest.json').read_text()) if (D/'manifest.json').exists() else 'inspect existing directory'}))
else:
 with (R/'rarity_residual_pilot_v1_controller.log').open('x') as f:p=subprocess.Popen([sys.executable,str(R/'research_round8_rarity_residual_pilot_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps({'launched':True,'pid':p.pid,'directory':str(D)}))
