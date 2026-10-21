import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'model_order_v2').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_model_order_v2_worker.py')],stdout=(R/'model_order_v2.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'job':'model_order_v2','pid':p.pid,'paid_usd':0}))
