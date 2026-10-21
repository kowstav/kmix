import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'word_softmax_queue_v1').exists();assert not (R/'word_softmax_v1').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_word_softmax_queue_worker.py')],stdout=(R/'word_softmax_queue_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'scope':'dependency queue, no overlapping GPU launch'}))
