import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'causal_sequence_v1').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_sequence_worker.py')],stdout=(R/'causal_sequence_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'gpu':1,'destination':str(R/'causal_sequence_v1')}))
