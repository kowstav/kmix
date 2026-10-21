def _hp_round7_prepare_confirmation():
    import pathlib, subprocess, json, os, shutil
    out=pathlib.Path('/kaggle/working/hp_round7')
    jobs=[]
    for name,lo,hi,gpu in [('c',100000000,102000000,'0'),('d',180000000,182000000,'1')]:
        prefix=out/(name+'2m')
        record=out/(name+'_probs.pid')
        if record.exists(): raise RuntimeError('Confirmation job already recorded: '+name)
        log=out/(name+'_probs.log')
        with log.open('w') as f:
            process=subprocess.Popen(['python','-u','/root/hp/tools/genprobs.py',str(lo),str(hi),str(prefix)],stdout=f,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'CUDA_VISIBLE_DEVICES':gpu,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
        record.write_text(str(process.pid))
        jobs.append({'slice':name,'lo':lo,'hi':hi,'gpu':gpu,'pid':process.pid,'log':str(log)})
    print(json.dumps({'jobs':jobs,'free_disk':shutil.disk_usage(out).free}))
_hp_round7_prepare_confirmation()
del _hp_round7_prepare_confirmation
