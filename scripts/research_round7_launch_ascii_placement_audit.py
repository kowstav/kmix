import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_ascii_placement_audit.py'
assert script.is_file() and not (out/'ascii_placement_audit_v1').exists(),'Do not duplicate'
assert not any(str(script) in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()),'Audit active'
with (out/'ascii_placement_audit_v1_controller.log').open('x') as log:
    p=subprocess.Popen(['python3','-u',str(script)],cwd=out,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_pid':p.pid,'job':'full ASCII placement diagnostic including literal i/I','codec':False,'paid_rental_usd':0,'deletions':[]}))
