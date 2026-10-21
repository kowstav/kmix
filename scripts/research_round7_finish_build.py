def _hp_finish_build():
    import pathlib,subprocess,json
    hp=pathlib.Path('/root/hp'); out=pathlib.Path('/kaggle/working/hp_round7'); lab=hp/'round7_lab'
    for line in (hp/'src/fx2-cmix-transformer-v1/build_and_construct_comp.sh').read_text().splitlines():
        if line.startswith(('SEED=', 'UPDATE_LIMIT=')): print(line)
    script=out/'finish_build_worker.py'
    script.write_text("import pathlib,subprocess,shutil,json\nhp=pathlib.Path('/root/hp'); out=pathlib.Path('/kaggle/working/hp_round7'); lab=hp/'round7_lab'\nsubprocess.run(['make','-j2','CC=clang++-17','CFLAGS_DEFINES=-DSEED=923 -DUPDATE_LIMIT=3000','cmix'],cwd=lab,check=True)\nshutil.copy2(lab/'cmix',out/'cmix_round7_baseline')\n(hp/'lexT').mkdir(exist_ok=True)\nif not (hp/'lexT/cmix').exists(): (hp/'lexT/cmix').symlink_to(lab/'cmix')\nw=hp/'gen/.tfweights'\nif not w.exists(): w.symlink_to(out/'reference.fx2tfwc2')\nprint(json.dumps({'build_complete':True,'bytes':(lab/'cmix').stat().st_size}),flush=True)\n")
    with (out/'build_lab_finish.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(script)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'build_lab_finish.pid').write_text(str(p.pid))
    print(json.dumps({'pid':p.pid}))
_hp_finish_build()
del _hp_finish_build
