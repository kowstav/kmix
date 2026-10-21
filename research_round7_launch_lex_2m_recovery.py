import pathlib, subprocess, json
out=pathlib.Path('/kaggle/working/hp_round7')
assert not (out/'lex_native_2m_recovered').exists() and not (out/'lex_native_2m_recovery_controller.log').exists(),'Refuse duplicate recovery'
running=subprocess.check_output(['ps','-eo','args'],text=True)
assert 'cmix_round7_lex_codebook ' not in running,'Inspect existing native job before launch'
with (out/'lex_native_2m_recovery_controller.log').open('w') as f:
    p=subprocess.Popen(['python','-u',str(out/'research_round7_recover_lex_2m_controller.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'recovery_controller_pid':p.pid,'maximum_native_jobs':2,'order':'decode C/D; regenerate lost A/B archives; decode A/B','no_deletions':True}))
