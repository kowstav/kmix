import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'atom_cache_v1').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_atom_cache_worker.py')],stdout=(R/'atom_cache_v1_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'atom_cache_v1','canonical_lexical_stream':True,'spending_usd':0,'deletions':[]}))
