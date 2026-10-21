import pathlib,subprocess,json,time
out=pathlib.Path('/kaggle/working/hp_round7');pre=out/'preserved'
for _ in range(720):
    if all((out/(n+'_word_association_root_v1_screen.json')).exists() for n in 'abcd'):break
    for n in 'abcd':
        log=out/(n+'_word_association_root_v1.log')
        if log.exists() and 'Traceback' in log.read_text():raise RuntimeError('Root experiment failed: '+n)
    time.sleep(5)
else:raise RuntimeError('Root timeout')
subprocess.run(['python3',str(out/'research_round7_word_newmention_screen.py'),'--self-test'],check=True)
jobs=[]
for n in 'abcd':
    log=out/(n+'_word_newmention_v1.log');dest=out/(n+'_word_newmention_v1_screen.json')
    if log.exists() or dest.exists():raise RuntimeError('Refuse duplicate '+n)
    raw=pre/f'slices/{n}2m.bin' if n in 'ab' else out/f'{n}2m.bin';cost=pre/f'runs/lex_{n}/cost.f32' if n in 'ab' else out/f'baseline_{n}/cost.f32'
    p=subprocess.Popen(['python3','-u',str(out/'research_round7_word_newmention_screen.py'),'--raw',str(raw),'--cost',str(cost),'--dictionary',str(pre/'gen/.dict'),'--out',str(dest)],stdout=log.open('w'),stderr=subprocess.STDOUT,start_new_session=True);jobs.append({'slice':n,'pid':p.pid})
(out/'word_newmention_v1_jobs.json').write_text(json.dumps(jobs,indent=2));print(json.dumps(jobs),flush=True)
