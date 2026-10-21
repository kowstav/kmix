import json,pathlib,subprocess,sys
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'native_inline_wide_v1'
if D.exists():
 print(json.dumps({'duplicate_not_launched':True,'manifest':json.loads((D/'manifest.json').read_text()) if (D/'manifest.json').exists() else 'directory exists; inspect before action'}))
else:
 with (R/'native_inline_wide_v1_controller.log').open('x') as f:
  p=subprocess.Popen([sys.executable,str(R/'research_round8_native_inline_wide_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps({'launched':True,'pid':p.pid,'directory':str(D),'log':str(R/'native_inline_wide_v1_controller.log')}))
