import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'adaptive_native_v1').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_adaptive_native_worker.py')],stdout=(R/'adaptive_native_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'fresh_offsets':[65000000,375000000]}))
