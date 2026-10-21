"""One detached identity trace worker, preserving all prior builds/results."""
import json,pathlib,subprocess
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_lex_finalbit_trace_worker.py'
assert script.is_file() and not (out/'lex_finalbit_trace_v1').exists() and not pathlib.Path('/root/hp/lex_finalbit_trace_v1').exists(), 'Do not duplicate or overwrite'
assert not any(str(script) in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()), 'Trace worker already active'
with (out/'lex_finalbit_trace_v1_controller.log').open('x') as log:
    p=subprocess.Popen(['python3','-u',str(script)],cwd=out,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_pid':p.pid,'job':'I05 lex final-bit identity trace prerequisite', 'neural_training':False,'paid_rental_usd':0,'deletions':[]}))
