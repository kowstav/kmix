import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');log=out/'word_root_controller.log'
if log.exists():raise RuntimeError('Refuse duplicate controller')
p=subprocess.Popen(['python3','-u',str(out/'research_round7_word_root_controller.py')],stdout=log.open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'root_controller':p.pid}))
