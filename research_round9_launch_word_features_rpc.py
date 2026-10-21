import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'word_features_v1').exists()
assert json.loads((R/'core_layer_gpu_v4/manifest.json').read_text())['status'].startswith('COMPLETE')
p=subprocess.Popen(['python3',str(R/'research_round9_word_feature_worker.py')],stdout=(R/'word_features_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'gpu':0,'scope':'18 spelling/glyph/grammar arms, causal combinations and matched controls'}))
