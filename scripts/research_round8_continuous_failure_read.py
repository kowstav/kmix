import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');log=R/'continuous_strength_v1_controller.log'
print(json.dumps({'log':log.read_text() if log.exists() else None,'processes':[x for x in subprocess.run(['ps','-eo','pid,etime,args'],capture_output=True,text=True).stdout.splitlines() if 'round8' in x]}))
