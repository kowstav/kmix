import pathlib,subprocess,json
root=pathlib.Path('/kaggle/working/hp_round7');script=root/'research_round7_constructor_skeleton.py'
assert json.loads((root/'constructor_split_v1/manifest.json').read_text())['status']=='COMPLETE'
assert script.is_file() and not (root/'constructor_skeleton_v1').exists(),'No duplicate skeleton experiment'
assert not any(str(script) in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()),'Already active'
with (root/'constructor_skeleton_v1_controller.log').open('x') as log:
    p=subprocess.Popen(['python3','-u',str(script)],cwd=root,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_pid':p.pid,'experiment':'I11b constructor skeleton framing-cost follow-up','neural_training':False,'paid_rental_usd':0,'deletions':[]}))
