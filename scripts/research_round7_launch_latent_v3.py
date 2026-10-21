import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_causal_latent_v3_screen.py'
assert script.is_file()
assert not (out/'causal_latent_words_v3').exists(),'V3 output already exists; inspect/reuse, never duplicate'
active=subprocess.check_output(['ps','-eo','args'],text=True)
assert not any(str(script) in s for s in active.splitlines()),'V3 already active'
log=(out/'causal_latent_v3_controller.log').open('x')
p=subprocess.Popen(['python3','-u',str(script)],cwd=out,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
log.close();print(json.dumps({'started_pid':p.pid,'job':'Fixed topic prior V3, B/C only, queued behind existing V2 and native recovery',
                              'neural_training':False,'paid_rental_usd':0,'deletions':[]}))
