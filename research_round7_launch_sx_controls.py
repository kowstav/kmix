def _hp_launch_sx_controls():
    import pathlib,subprocess,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    if not (out/'cmix_round7_sx_control').exists():raise RuntimeError('Control build incomplete')
    if (out/'sx_control_controller.pid').exists():raise RuntimeError('Control controller already exists')
    with (out/'sx_control_controller.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(out/'research_round7_sx_control_controller.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'sx_control_controller.pid').write_text(str(p.pid))
    print(json.dumps({'pid':p.pid}))
_hp_launch_sx_controls()
del _hp_launch_sx_controls
