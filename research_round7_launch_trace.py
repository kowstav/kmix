def _hp_launch_trace():
    import pathlib,subprocess,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    if not (out/'cmix_round7_trace').exists():raise RuntimeError('Trace build incomplete')
    if (out/'trace_controller.pid').exists():raise RuntimeError('Trace controller already exists')
    with (out/'trace_controller.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(out/'research_round7_trace_controller.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'trace_controller.pid').write_text(str(p.pid))
    print(json.dumps({'pid':p.pid,'trace_build_log':(out/'build_trace.log').read_text()[-500:]}))
_hp_launch_trace()
del _hp_launch_trace
