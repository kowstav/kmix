import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');assert not (out/'lex_native_controller.log').exists()
with (out/'lex_native_controller.log').open('w') as f:p=subprocess.Popen(['python','-u',str(out/'research_round7_lex_native_controller.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'lex_native_controller_pid':p.pid,'maximum_concurrent_cmix':2,'checks':'forced full compile, native original checkpoint probabilities, A/B/C/D exact raw round trips, CPU and peak RSS'}))
