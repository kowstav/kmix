import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'packing_differential_v1').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_packing_differential_worker.py')],stdout=(R/'packing_differential_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'job':'packing_differential_v1','pid':p.pid,'gpu':0,'paid_usd':0}))
