import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');assert not (out/'causal_latent_words_controller.log').exists(),'Refuse duplicate screen'
with (out/'causal_latent_words_controller.log').open('w') as f:
    p=subprocess.Popen(['python','-u',str(out/'research_round7_causal_latent_word_screen.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'causal_latent_screen_pid':p.pid,'normalization_and_root_accounting_tests_before_corpus':True,'no_neural_training':True,'no_stored_topic_selector_or_table':True}))
