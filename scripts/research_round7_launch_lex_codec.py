import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_lex_codec_worker.py'
assert not (out/'lex_codec.log').exists(),'Refuse duplicate launch'
with (out/'lex_codec.log').open('w') as log:
    p=subprocess.Popen(['python','-u',str(script)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'lex_codec_pid':p.pid,'no_neural_training':True,'original_model_unchanged':True}))
