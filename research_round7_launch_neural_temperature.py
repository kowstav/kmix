def _hp_launch_neural_temperature():
    import pathlib,subprocess,os,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    jobs=[]
    for name,gpu in [('a',0),('b',1),('c',0),('d',1)]:
        # Two short sequential batches, avoiding unnecessary duplicate GPU loads.
        if name in ['c','d']:continue
        env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
        with (out/(name+'_neural_temperature.log')).open('w') as log:
            p=subprocess.Popen(['python','-u',str(out/'research_round7_neural_temperature.py'),'--slice',name,'--out',str(out),'--device','cuda:'+str(gpu)],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        jobs.append({'slice':name,'pid':p.pid,'gpu':gpu})
    print(json.dumps(jobs))
_hp_launch_neural_temperature()
del _hp_launch_neural_temperature
