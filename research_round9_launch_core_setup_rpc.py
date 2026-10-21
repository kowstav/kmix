import pathlib,subprocess,json,os
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'core_setup_v1').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_core_setup_worker.py')],stdout=(R/'core_setup_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
(R/'core_setup_launch.json').write_text(json.dumps({'pid':p.pid,'session':355735431}));print(json.dumps({'pid':p.pid}))
