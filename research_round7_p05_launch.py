import json,pathlib,subprocess
r=pathlib.Path('/kaggle/working/hp_round7');assert not (r/'full_stream_regen_v1').exists()
log=(r/'full_stream_regen_v1_controller.log').open('x');p=subprocess.Popen(['python',str(r/'research_round7_p05_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'p05_pid':p.pid,'scope':'model-free preparation, not full coding or training-prior regeneration'}))
