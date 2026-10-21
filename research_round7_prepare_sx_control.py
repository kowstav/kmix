def _hp_prepare_sx_control():
    import pathlib,shutil,subprocess,json
    hp=pathlib.Path('/root/hp');out=pathlib.Path('/kaggle/working/hp_round7');dst=hp/'round7_sx_control'
    if dst.exists():raise RuntimeError('Existing topology control tree')
    shutil.copytree(hp/'round7_lab',dst)
    subprocess.run(['python',str(hp/'tools/sxpatch.py')],cwd=dst,check=True)
    worker=out/'build_sx_control_worker.py'
    worker.write_text("import pathlib,subprocess,shutil,json\nhp=pathlib.Path('/root/hp');out=pathlib.Path('/kaggle/working/hp_round7');dst=hp/'round7_sx_control'\nsubprocess.run(['make','-j1','CC=clang++-17','CFLAGS_DEFINES=-DSEED=923 -DUPDATE_LIMIT=3000','cmix'],cwd=dst,check=True)\nshutil.copy2(dst/'cmix',out/'cmix_round7_sx_control')\nprint('SX_CONTROL_BUILD_COMPLETE',flush=True)\n")
    with (out/'build_sx_control.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(worker)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'pid':p.pid}))
_hp_prepare_sx_control()
del _hp_prepare_sx_control
