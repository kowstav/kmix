import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'native_promotion_v1').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_native_promotion_worker.py')],stdout=(R/'native_promotion_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'job':'native_promotion_v1','pid':p.pid,'paid_usd':0}))
