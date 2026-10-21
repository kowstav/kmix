import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_bit_placement_residual.py'
assert script.is_file() and not (out/'bit_placement_residual_pilot_v1').exists(),'No duplicate pilot'
assert json.loads((out/'lex_finalbit_trace_v2/results.json').read_text())['status']=='PASS','Both native identity/decode gates required'
assert not any(str(script) in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()),'Pilot active'
with (out/'bit_placement_residual_pilot_v1_controller.log').open('x') as log:
    p=subprocess.Popen(['python3','-u',str(script)],cwd=out,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_pid':p.pid,'job':'I05 quantized final-bit residual placement pilot on native A/B32K traces','neural_training':False,'paid_rental_usd':0,'deletions':[]}))
