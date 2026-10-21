import pathlib,subprocess,json,os
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'native_hidden_trace_v1';assert not D.exists(),'Existing experiment: inspect and reuse'
log=(R/'native_hidden_trace_v1_controller.log').open('x');p=subprocess.Popen(['python','-u',str(R/'research_round8_native_hidden_trace_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'launched_pid':p.pid,'experiment':'native_hidden_trace_v1','retraining':False,'paid_rental_usd':0,'deletions':[]}))
