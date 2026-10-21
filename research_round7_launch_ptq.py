import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7')
for worker,name in [('research_round7_ptq_codec_worker.py','ptq_codec.log'),('research_round7_ptq_native_controller.py','ptq_native_controller.log')]:
    log=out/name
    if log.exists():raise RuntimeError('Refuse duplicate PTQ worker')
    p=subprocess.Popen(['python3','-u',str(out/worker)],stdout=log.open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'worker':worker,'pid':p.pid}))
