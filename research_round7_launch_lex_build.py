import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7')
assert not (out/'lex_build.log').exists(),'Refuse duplicate launch'
with (out/'lex_build.log').open('w') as log:
    p=subprocess.Popen(['python','-u',str(out/'research_round7_lex_build_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'lex_build_pid':p.pid,'log':'lex_build.log'}))
