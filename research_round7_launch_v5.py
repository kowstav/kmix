import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7')
print('WEIGHTS_LOADER_PATHS',[str(p) for p in pathlib.Path('/root/hp/round7_lab').rglob('*weights*')])
print('MAKEFILE',(pathlib.Path('/root/hp/round7_lab/makefile').read_text())[-8000:])
log=out/'v5_codec.log'
if log.exists():raise RuntimeError('Refuse duplicate codec worker')
p=subprocess.Popen(['python3','-u',str(out/'research_round7_v5_worker.py')],stdout=log.open('w'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started':p.pid,'log':str(log)}))
