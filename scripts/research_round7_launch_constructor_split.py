import pathlib,subprocess,json
root=pathlib.Path('/kaggle/working/hp_round7');script=root/'research_round7_constructor_split.py'
assert script.is_file() and not (root/'constructor_split_v1').exists(),'Reuse existing result/job; no duplicate'
assert not any(str(script) in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()),'Already active'
with (root/'constructor_split_v1_controller.log').open('x') as log:
    job=subprocess.Popen(['python3','-u',str(script)],cwd=root,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_pid':job.pid,'experiment':'I11 raw-reversible paid constructor/content streams',
                  'neural_training':False,'paid_rental_usd':0,'deletions':[]}))
