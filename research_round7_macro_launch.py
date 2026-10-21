import pathlib,subprocess,json
r=pathlib.Path('/kaggle/working/hp_round7');assert not (r/'macro_packets_v1').exists();log=(r/'macro_packets_v1_controller.log').open('x');p=subprocess.Popen(['python',str(r/'research_round7_macro_screen.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'macro_pid':p.pid}))
