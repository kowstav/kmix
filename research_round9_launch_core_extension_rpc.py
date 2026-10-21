import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'core_extension_v1').exists();assert json.loads((R/'hidden_sequence_v2/manifest.json').read_text())['status'].startswith('COMPLETE')
p=subprocess.Popen(['python3',str(R/'research_round9_core_extension_worker.py')],stdout=(R/'core_extension_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'gpu':1,'checkpoint_scratch':'/root/hp_round9/core_extension_v1'}))
