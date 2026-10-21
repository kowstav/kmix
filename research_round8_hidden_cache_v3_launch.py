import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'hidden_cache_v3_controller_status.json').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_hidden_cache_v3_controller.py')],stdout=(R/'hidden_cache_v3_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'hidden_cache_v2','dependency':'native_hidden_trace_v4 exact identity','no_retraining':True,'paid_rental_usd':0}))
