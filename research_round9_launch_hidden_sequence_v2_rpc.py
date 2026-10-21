import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'hidden_sequence_v2').exists();assert json.loads((R/'causal_sequence_v1/manifest.json').read_text())['status'].startswith('COMPLETE')
p=subprocess.Popen(['python3',str(R/'research_round9_hidden_sequence_worker_v2.py')],stdout=(R/'hidden_sequence_v2.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'gpu':1}))

