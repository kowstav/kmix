import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');assert not (out/'causal_latent_v2_controller.log').exists(),'Refuse duplicate corrected screen'
with (out/'causal_latent_v2_controller.log').open('w') as f:
    p=subprocess.Popen(['python','-u',str(out/'research_round7_causal_latent_word_v2_screen.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'corrected_causal_latent_pid':p.pid,'activation_after_complete_marker':True,'old_evidence_preserved':True}))
