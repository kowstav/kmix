import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_idea_arch_screen.py'
assert script.is_file() and not (out/'idea_arch_screens_v1').exists(),'Prior evidence exists; reuse rather than duplicate'
assert not any(str(script) in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()),'Screen already active'
log=(out/'idea_arch_screens_v1_controller.log').open('x')
p=subprocess.Popen(['python3','-u',str(script)],cwd=out,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
log.close();print(json.dumps({'started_pid':p.pid,'job':'I01/I03 dictionary-derived echo and matched controls, A/B/C/D; I02 lag diagnostics separate pending',
                              'neural_training':False,'paid_rental_usd':0,'deletions':[]}))
