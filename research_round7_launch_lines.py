def _hp_launch_lines():
    import pathlib,subprocess,os,json
    out=pathlib.Path('/kaggle/working/hp_round7');jobs=[]
    for name in ['a','b']:
        worker=out/(name+'_line_worker.py')
        worker.write_text(f'''import pathlib,subprocess
out=pathlib.Path('/kaggle/working/hp_round7')
for masked,exact in [(False,True),(False,False),(True,False)]:
    tag='exact' if exact else 'masked_edit' if masked else 'edit'
    cmd=['python',str(out/'research_round7_line_edit_screen.py'),'--slice','/root/hp/slices/{name}2m.bin','--cost','/root/hp/runs/lex_{name}/cost.f32','--dictionary','/root/hp/gen/.dict','--out',str(out/('{name}_line_'+tag+'.json'))]
    if masked:cmd.append('--mask-digits')
    if exact:cmd.append('--exact')
    subprocess.run(cmd,check=True)
print('LINE_SCREENS_COMPLETE',flush=True)
''')
        env={**os.environ,'HP_EDIT_KERNEL':str(out/'hp_edit_kernel.so'),'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
        with (out/(name+'_line.log')).open('w') as log:
            p=subprocess.Popen(['python','-u',str(worker)],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        jobs.append({'slice':name,'pid':p.pid})
    print(json.dumps(jobs))
_hp_launch_lines()
del _hp_launch_lines
