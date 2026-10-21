import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_lex_finalbit_2m_worker.py'
assert script.is_file() and not (out/'lex_finalbit_2m_v1').exists(),'No duplicate2M final-bit collection'
assert not any(str(script) in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()),'Collector active'
with (out/'lex_finalbit_2m_v1_controller.log').open('x') as log:
    p=subprocess.Popen(['python3','-u',str(script)],cwd=out,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_pid':p.pid,'job':'collect4 matched2M final-bit traces only after32K identity/decode PASS','max_native_processes':2,'paid_rental_usd':0,'deletions':[]}))
