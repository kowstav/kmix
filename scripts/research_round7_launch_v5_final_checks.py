import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7')
for worker,logname in [('research_round7_v5_package_worker.py','v5_package_retry.log'),('research_round7_v5_inference_worker.py','v5_inference_controller.log')]:
    log=out/logname
    if log.exists():raise RuntimeError('Refuse duplicate worker: '+worker)
    p=subprocess.Popen(['python3','-u',str(out/worker)],stdout=log.open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'started':worker,'pid':p.pid}))
