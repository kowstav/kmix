def _hp_launch_context_atlas():
    import pathlib,subprocess,os,json
    out=pathlib.Path('/kaggle/working/hp_round7')
    worker=out/'word_context_atlas_worker.py'
    worker.write_text("import pathlib,subprocess,time\nout=pathlib.Path('/kaggle/working/hp_round7')\nfor name in ['a','b','c','d']:\n    if name in ['c','d']:\n        for _ in range(240):\n            if 'CONFIRMATION_BASELINES_COMPLETE' in (out/'confirmation_controller.log').read_text():break\n            time.sleep(5)\n        else:raise RuntimeError('Waiting for native baseline timed out')\n    subprocess.run(['python',str(out/'research_round7_word_context_atlas.py'),'--slice',name,'--out',str(out)],check=True)\nprint('WORD_CONTEXT_ATLASES_COMPLETE',flush=True)\n")
    env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
    with (out/'word_context_atlas.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(worker)],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'word_context_atlas.pid').write_text(str(p.pid))
    print(json.dumps({'pid':p.pid}))
_hp_launch_context_atlas()
del _hp_launch_context_atlas
