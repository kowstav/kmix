import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');log=out/'v5_package.log'
if log.exists():raise RuntimeError('Refuse duplicate package worker')
p=subprocess.Popen(['python3','-u',str(out/'research_round7_v5_package_worker.py')],stdout=log.open('w'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_package_worker':p.pid}))
hp=pathlib.Path('/root/hp')
for name in ['src/runner.cpp','src/predictor.cpp']:
    s=(hp/'cand_final2'/name).read_text();print('CAND_LAB_REFERENCES',name,[l.strip() for l in s.splitlines() if 'LAB_' in l][:30])
print('LAB_RAW_REFERENCES',[l.strip() for l in (hp/'round7_lab/src/runner.cpp').read_text().splitlines() if 'LAB_RAW' in l])
