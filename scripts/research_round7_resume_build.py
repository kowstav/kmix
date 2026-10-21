def _hp_round7_resume_build():
    import pathlib,shutil,subprocess,json
    hp=pathlib.Path('/root/hp'); out=pathlib.Path('/kaggle/working/hp_round7'); lab=hp/'round7_lab'
    # The initial copy excluded every directory named models. Restore only the
    # source model directory; shipped neural checkpoints stay in their own tree.
    if not (lab/'src/models').exists(): shutil.copytree(hp/'src/fx2-cmix-transformer-v1/src/models',lab/'src/models')
    code=r'''
import pathlib,subprocess,shutil,json
hp=pathlib.Path('/root/hp'); out=pathlib.Path('/kaggle/working/hp_round7'); lab=hp/'round7_lab'
subprocess.run(['python',str(hp/'tools/lexpatch.py')],cwd=lab,check=True)
mf=lab/'makefile'; mf.write_text(mf.read_text().replace('\trm -f *.o\n','\t@true\n'))
subprocess.run(['make','-j2','CC=clang++-17'],cwd=lab,check=True)
shutil.copy2(lab/'cmix',out/'cmix_round7_baseline')
(hp/'lexT').mkdir(exist_ok=True)
(hp/'lexT/cmix').symlink_to(lab/'cmix')
print(json.dumps({'build_complete':True,'bytes':(lab/'cmix').stat().st_size}),flush=True)
'''
    script=out/'resume_build_worker.py'; script.write_text(code)
    with (out/'build_lab_resume.log').open('w') as log:
        p=subprocess.Popen(['python','-u',str(script)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'build_lab_resume.pid').write_text(str(p.pid))
    print(json.dumps({'pid':p.pid,'restored_model_source_files':len(list((lab/'src/models').iterdir()))}))
_hp_round7_resume_build()
del _hp_round7_resume_build
