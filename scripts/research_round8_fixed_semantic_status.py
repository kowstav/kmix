import pathlib,json,subprocess
D=pathlib.Path('/kaggle/working/hp_round8/fixed_semantic_v1');m=json.loads((D/'manifest.json').read_text())
print(json.dumps({'manifest':m,'active_processes':[x for x in subprocess.run(['ps','-eo','pid,etime,args'],capture_output=True,text=True).stdout.splitlines() if 'round8' in x]}))
