"""Read-only I11 status; one compact snapshot, no relaunch."""
import pathlib,json,subprocess,shutil
r=pathlib.Path('/kaggle/working/hp_round7');d=r/'constructor_split_v1';out={}
for name in ['manifest.json','summary.json']:
    p=d/name
    if p.is_file():out[name]=json.loads(p.read_text())
p=r/'constructor_split_v1_controller.log';out['log_tail']=p.read_text()[-1500:] if p.is_file() else None
out['active']='\n'.join(s for s in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'constructor_split.py' in s)
out['persistent_free_bytes']=shutil.disk_usage('/kaggle/working').free
print(json.dumps(out,indent=2))
