import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');assert not (out/'frozen_logits_pilot_controller.log').exists(),'Refuse duplicate pilot'
probe=json.loads((out/'frozen_shape_probe_results.json').read_text());assert probe['runtime_import_succeeded'] and all(r['strict_structure_load'] for r in probe['models'])
with (out/'frozen_logits_pilot_controller.log').open('w') as f:
    p=subprocess.Popen(['python','-u',str(out/'research_round7_frozen_logits_pilot_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'frozen_logits_pilot_pid':p.pid,'queued_after_existing_native_recovery':True,'native_jobs_in_pilot':1,'true_priors_required':True,'no_SGD':True,'paid_rental_usd':0}))
