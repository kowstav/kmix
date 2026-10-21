import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');preserved=out/'preserved'
subprocess.run(['python3',str(out/'research_round7_word_association_screen.py'),'--self-test'],check=True)
jobs=[]
for name in 'abcd':
    log=out/(name+'_word_association_v2.log');dest=out/(name+'_word_association_v2_screen.json')
    if log.exists() or dest.exists():raise RuntimeError('Refuse duplicate association experiment '+name)
    raw=preserved/f'slices/{name}2m.bin' if name in 'ab' else out/f'{name}2m.bin'
    costs=preserved/f'runs/lex_{name}/cost.f32' if name in 'ab' else out/f'baseline_{name}/cost.f32'
    cmd=['python3','-u',str(out/'research_round7_word_association_screen.py'),'--raw',str(raw),'--cost',str(costs),'--dictionary',str(preserved/'gen/.dict'),'--out',str(dest)]
    p=subprocess.Popen(cmd,stdout=log.open('w'),stderr=subprocess.STDOUT,start_new_session=True)
    jobs.append({'slice':name,'pid':p.pid,'log':str(log),'out':str(dest)})
(out/'word_association_v2_jobs.json').write_text(json.dumps(jobs,indent=2));print(json.dumps(jobs))
