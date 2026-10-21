import pathlib,json,subprocess,os
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'word_softmax_v1').exists()
j=json.loads((R/'core_extension_v1/manifest.json').read_text());assert j['status'].startswith('COMPLETE'),'Reuse GPU1 training until it completes; no overlapping launch'
p=subprocess.Popen(['python3',str(R/'research_round9_word_softmax_worker.py')],stdout=(R/'word_softmax_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'gpu':1,'scope':'eight normalized full word-softmax/composer runs'}))
