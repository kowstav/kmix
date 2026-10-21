import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'core_training_v2').exists();assert json.loads((R/'full_word_alignment_v2/manifest.json').read_text())['status']=='COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS'
p=subprocess.Popen(['python3',str(R/'research_round9_core_training_worker_v2.py')],stdout=(R/'core_training_v2.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'gpu':0}))

