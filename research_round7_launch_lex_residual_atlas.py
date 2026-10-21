import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7')
assert not (out/'lex_residual_atlas').exists() and not (out/'lex_residual_atlas.log').exists(),'Refuse duplicate atlas'
with (out/'lex_residual_atlas.log').open('w') as f:
    p=subprocess.Popen(['python','-u',str(out/'research_round7_lex_residual_atlas.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'lex_residual_atlas_pid':p.pid,'no_predictor_or_weight_changes':True,'no_deletions':True}))
