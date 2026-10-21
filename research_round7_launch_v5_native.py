import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');log=out/'v5_native.log'
if log.exists():raise RuntimeError('Refuse duplicate native worker')
p=subprocess.Popen(['python3','-u',str(out/'research_round7_v5_native_worker.py')],stdout=log.open('w'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_native_v5_worker':p.pid}))
