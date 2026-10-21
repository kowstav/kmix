import pathlib,json,subprocess
root=pathlib.Path('/kaggle/working/hp_round7');d=root/'constructor_skeleton_v2';out={}
p=d/'manifest.json'
if p.is_file():out['manifest']=json.loads(p.read_text())
p=d/'summary.json'
if p.is_file():out['completed']=[{'slice':r['slice'],'saved_bytes':[v['bytes_saved_before_incremental_decoder'] for v in r['screen_rows']]} for r in json.loads(p.read_text())]
p=root/'constructor_skeleton_v2_controller.log';out['log_tail']=p.read_text()[-1800:] if p.is_file() else None
out['active']='\n'.join(s for s in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'constructor_skeleton_v2.py' in s)
print(json.dumps(out,indent=2))
