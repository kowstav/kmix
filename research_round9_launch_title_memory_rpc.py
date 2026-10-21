import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'title_memory_v1').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_title_memory_worker.py')],stdout=(R/'title_memory_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'job':'title_memory_v1','pid':p.pid}))
