import pathlib,subprocess,json,time
out=pathlib.Path('/kaggle/working/hp_round7');preserved=out/'preserved'
for _ in range(720):
    results=[out/(n+'_word_association_v2_screen.json') for n in 'abcd']
    if all(p.exists() for p in results):break
    for n in 'abcd':
        if 'Traceback' in (out/(n+'_word_association_v2.log')).read_text():raise RuntimeError('Suffix experiment failed: '+n)
    time.sleep(5)
else:raise RuntimeError('Suffix experiments did not finish')
subprocess.run(['python3',str(out/'research_round7_word_association_root_screen.py'),'--self-test'],check=True)
jobs=[]
for name in 'abcd':
    log=out/(name+'_word_association_root_v1.log');dest=out/(name+'_word_association_root_v1_screen.json')
    if log.exists() or dest.exists():raise RuntimeError('Refuse duplicate root experiment '+name)
    raw=preserved/f'slices/{name}2m.bin' if name in 'ab' else out/f'{name}2m.bin'
    cost=preserved/f'runs/lex_{name}/cost.f32' if name in 'ab' else out/f'baseline_{name}/cost.f32'
    cmd=['python3','-u',str(out/'research_round7_word_association_root_screen.py'),'--raw',str(raw),'--cost',str(cost),'--dictionary',str(preserved/'gen/.dict'),'--out',str(dest)]
    p=subprocess.Popen(cmd,stdout=log.open('w'),stderr=subprocess.STDOUT,start_new_session=True);jobs.append({'slice':name,'pid':p.pid})
(out/'word_association_root_v1_jobs.json').write_text(json.dumps(jobs,indent=2));print(json.dumps(jobs),flush=True)
print('ROOT_JOBS_LAUNCHED',flush=True)
