def _hp_round7_audit():
    import os, json, shutil, subprocess, pathlib
    result = {'cwd': os.getcwd(), 'disks': {}, 'environment': {}}
    for root in ['/kaggle/working','/root/hp','/tmp']:
        if os.path.exists(root):
            d=shutil.disk_usage(root)
            result['disks'][root]={'total':d.total,'used':d.used,'free':d.free}
    commands = {
        'gpu':['nvidia-smi','--query-gpu=name,memory.used,memory.total,utilization.gpu','--format=csv,noheader'],
        'processes':['ps','-eo','pid,ppid,etime,%cpu,%mem,args','--sort=-%cpu'],
        'working_sizes':['du','-h','--max-depth=2','/kaggle/working'],
        'hp_sizes':['du','-h','--max-depth=2','/root/hp'],
        'large_files':['find','/kaggle/working','/root/hp','-type','f','-size','+100M','-printf','%s\t%p\n'],
        'root_listing':['ls','-la','/root/hp'],
    }
    for name, command in commands.items():
        try:
            r=subprocess.run(command,capture_output=True,text=True,timeout=25)
            result[name]={'returncode':r.returncode,'stdout':r.stdout[:50000],'stderr':r.stderr[:2000]}
        except Exception as e: result[name]={'error':type(e).__name__+': '+str(e)}
    print(json.dumps(result))
_hp_round7_audit()
del _hp_round7_audit
