def _hp_round7_launch_fields():
    import pathlib,subprocess,os,json
    out=pathlib.Path('/kaggle/working/hp_round7'); jobs=[]
    for name in ['a','b']:
        result=out/(name+'_field_screen.json')
        if result.exists(): raise RuntimeError('Screen result already exists: '+name)
        with (out/(name+'_field_screen.log')).open('w') as log:
            cmd=['python','-u',str(out/'research_round7_field_screen.py'),'--slice',f'/root/hp/slices/{name}2m.bin','--cost',f'/root/hp/runs/lex_{name}/cost.f32','--dictionary','/root/hp/gen/.dict','--json',str(result),'--events-jsonl',str(out/(name+'_field_events.jsonl'))]
            p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
        (out/(name+'_field_screen.pid')).write_text(str(p.pid))
        jobs.append({'slice':name,'pid':p.pid})
    print(json.dumps(jobs))
_hp_round7_launch_fields()
del _hp_round7_launch_fields
