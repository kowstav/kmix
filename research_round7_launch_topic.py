import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');assert not (out/'topic_selector.log').exists()
with (out/'topic_selector.log').open('w') as f:p=subprocess.Popen(['python','-u',str(out/'research_round7_topic_selector_screen.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'topic_screen_pid':p.pid,'models_frozen_from':'A/B','confirmation':'C/D','selectors_explicitly_priced':True,'neural_training':False}))
