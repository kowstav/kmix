import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'error_memory_v1').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_error_memory_worker.py')],stdout=(R/'error_memory_v1_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'error_memory_v1','dependency':'existing atom_cache_v1 canonical native exports; no duplicate inference','spending_usd':0,'deletions':[]}))
