import pathlib,json,subprocess,shutil
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'native_hidden_trace_v2';m=json.loads((D/'manifest.json').read_text())
print(json.dumps({**{k:m.get(k) for k in ['status','stage','pid','error','exports','controls']},'controller_tail':(R/'native_hidden_trace_v2_controller.log').read_text(errors='replace')[-700:],'active':[s for s in subprocess.run(['ps','-eo','pid,etime,args'],capture_output=True,text=True).stdout.splitlines() if 'native_hidden' in s and 'jupyter' not in s],'free_disk_bytes':shutil.disk_usage('/kaggle/working').free}))
