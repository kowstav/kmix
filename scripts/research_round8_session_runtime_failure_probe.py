import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');d={}
for n in ['atom_fit_resume_v1','error_memory_resume_v1','canonical_cost_atlas_v1']:
 p=R/(n+'_controller.log');d[n+'_log_tail']=p.read_text()[-5000:] if p.exists() else None
for n in ['memory.max','memory.current','memory.peak','memory.events']:
 p=pathlib.Path('/sys/fs/cgroup')/n;d[n]=p.read_text() if p.exists() else None
for pid in [109,117,124]:
 p=pathlib.Path('/proc')/str(pid)/'status';d[str(pid)]=p.read_text() if p.exists() else 'not present'
d['memory']=subprocess.check_output(['free','-b'],text=True);d['processes']=subprocess.check_output(['ps','-eo','pid,ppid,stat,pcpu,rss,args'],text=True)
print(json.dumps(d))
