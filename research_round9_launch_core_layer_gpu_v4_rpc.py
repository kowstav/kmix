import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'core_layer_gpu_v4').exists();assert json.loads((R/'core_layer_gpu_v3/manifest.json').read_text())['status'].startswith('COMPLETE')
p=subprocess.Popen(['python3',str(R/'research_round9_core_layer_gpu_worker_v4.py')],stdout=(R/'core_layer_gpu_v4.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'gpu':0}))
