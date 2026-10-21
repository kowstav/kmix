import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_frozen_logits_pilot_v2_worker.py'
assert script.is_file()
assert not (out/'frozen_logits_pilot_v2').exists() and not (out/'frozen_logits_pilot_v2_setup.json').exists(),'V2 evidence exists; inspect/reuse, do not duplicate'
active=subprocess.check_output(['ps','-eo','args'],text=True)
assert not any(str(script) in s or '/cmix_round7_' in s for s in active.splitlines()),'Pilot/native process already active'
log=(out/'frozen_logits_pilot_v2_controller.log').open('x')
p=subprocess.Popen(['python3','-u',str(script)],cwd=out,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
log.close();print(json.dumps({'started_pid':p.pid,'job':'F01 repaired native/GPU pilot; one native process at a time',
                              'neural_training':False,'paid_rental_usd':0,'deletions':[]}))
