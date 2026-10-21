import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'native_stage_fit_v1').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_native_stage_fit_worker.py')],stdout=(R/'native_stage_fit_v1_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'native_stage_fit_v1','depends_on':'native_stage_trace_v1','paid_spending_usd':0,'deletions':[]}))
