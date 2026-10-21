import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'core_pipeline_profile_v1').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_core_pipeline_profile_worker.py')],stdout=(R/'core_pipeline_profile_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'job':'core_pipeline_profile_v1','pid':p.pid,'waits_for_GPU0_training_completion':True}))
