import json,os,pathlib,shutil,subprocess,time
R=pathlib.Path('/kaggle/working/hp_round8')
print(json.dumps({'utc_unix':time.time(),'disk_free':shutil.disk_usage(R).free,'gpu':subprocess.run(['nvidia-smi','--query-gpu=index,name,memory.total,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout,'processes':subprocess.run(['ps','-eo','pid,ppid,etime,pcpu,pmem,args'],capture_output=True,text=True).stdout[-18000:],'memory':pathlib.Path('/proc/meminfo').read_text()[:700],'round9_exists':pathlib.Path('/kaggle/working/hp_round9').exists()}))
