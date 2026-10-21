import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'core_pipeline_profile_v2').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_core_pipeline_profile_v2_worker.py')],stdout=(R/'core_pipeline_profile_v2.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'job':'core_pipeline_profile_v2','pid':p.pid,'gpu':0,'paid_usd':0}))
