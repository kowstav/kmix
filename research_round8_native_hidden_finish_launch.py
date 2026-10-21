import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'native_hidden_trace_v2').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_native_hidden_finish_worker.py')],stdout=(R/'native_hidden_trace_v2_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'launched_pid':p.pid,'experiment':'native_hidden_trace_v2','reused_completed_build':True,'deletions':[]}))
