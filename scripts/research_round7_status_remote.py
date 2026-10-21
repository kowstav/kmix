def _hp_round7_status():
    import pathlib,os,json,subprocess,shutil
    out=pathlib.Path('/kaggle/working/hp_round7')
    result={'free_disk':shutil.disk_usage(out).free,'logs':{},'pids':{},'files':[]}
    for p in out.glob('*.log'): result['logs'][p.name]=p.read_text(errors='replace')[-3000:]
    for p in out.glob('*.pid'):
        pid=int(p.read_text()); stat=pathlib.Path('/proc')/str(pid)/'stat'
        result['pids'][p.name]={'pid':pid,'exists':stat.exists(),'state':stat.read_text().split()[2] if stat.exists() else None}
    for p in out.iterdir(): result['files'].append({'name':p.name,'size':p.stat().st_size,'is_dir':p.is_dir()})
    for binary in ['/root/hp/lexT/cmix','/root/hp/lexSX2/cmix','/root/hp/lexFM/cmix']:
        p=pathlib.Path(binary); result[binary]={'exists':p.exists(),'bytes':p.stat().st_size if p.exists() else None}
    gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True)
    result['gpu']=gpu.stdout
    print(json.dumps(result))
_hp_round7_status()
del _hp_round7_status
