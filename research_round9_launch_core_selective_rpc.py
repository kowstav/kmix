import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'core_selective_v1').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_core_selective_worker.py')],stdout=(R/'core_selective_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'job':'core_selective_v1','pid':p.pid,'gpu':1,'paid_usd':0}))
