def _hp_launch_confirmation_screens():
    import pathlib,subprocess,os,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    if (out/'corrected_confirmation_screens.pid').exists():raise RuntimeError('Confirmation scorer already exists')
    env={**os.environ,'HP_EDIT_KERNEL':str(out/'hp_edit_kernel.so'),'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
    with (out/'corrected_confirmation_screens.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(out/'research_round7_confirmation_screens_worker.py')],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'corrected_confirmation_screens.pid').write_text(str(p.pid));print(json.dumps({'pid':p.pid}))
_hp_launch_confirmation_screens()
del _hp_launch_confirmation_screens
