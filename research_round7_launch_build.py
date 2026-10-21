def _hp_round7_launch_build():
    import pathlib,subprocess,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    with (out/'build_lab.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(out/'research_round7_build_lab_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'build_lab.pid').write_text(str(p.pid))
    print(json.dumps({'pid':p.pid,'log':str(out/'build_lab.log')}))
_hp_round7_launch_build()
del _hp_round7_launch_build
