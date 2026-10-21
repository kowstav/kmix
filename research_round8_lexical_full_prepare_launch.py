import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'lexical_full_prepare_v1').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_lexical_full_prepare_worker.py')],stdout=(R/'lexical_full_prepare_v1_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'lexical_full_prepare_v1','models_preserved':True,'spending_usd':0,'deletions':[]}))
