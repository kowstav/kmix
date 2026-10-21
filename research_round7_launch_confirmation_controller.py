def _hp_round7_launch_controller():
    import pathlib,subprocess,os,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    if (out/'confirmation_controller.pid').exists(): raise RuntimeError('Controller already recorded')
    with (out/'confirmation_controller.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(out/'research_round7_confirmation_controller.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'confirmation_controller.pid').write_text(str(p.pid))
    print(json.dumps({'pid':p.pid}))
_hp_round7_launch_controller()
del _hp_round7_launch_controller
