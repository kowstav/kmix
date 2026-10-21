import json,pathlib,subprocess
r=pathlib.Path('/kaggle/working/hp_round7');assert json.loads((r/'full_stream_regen_v1/manifest.json').read_text())['status']=='FAIL';assert not (r/'full_stream_regen_v2').exists()
log=(r/'full_stream_regen_v2_controller.log').open('x');p=subprocess.Popen(['python',str(r/'research_round7_p05_v2_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'p05_v2_pid':p.pid,'first_failure_preserved':True}))
