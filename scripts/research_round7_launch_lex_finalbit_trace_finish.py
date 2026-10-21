import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_lex_finalbit_trace_finish.py'
assert script.is_file() and not (out/'lex_finalbit_trace_v2').exists(),'No duplicate repair'
assert not any(str(script) in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()),'Repair active'
with (out/'lex_finalbit_trace_v2_controller.log').open('x') as log:
    p=subprocess.Popen(['python3','-u',str(script)],cwd=out,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_pid':p.pid,'job':'native final-bit trace V2; reuse build and retain V1 failure','paid_rental_usd':0,'deletions':[]}))
