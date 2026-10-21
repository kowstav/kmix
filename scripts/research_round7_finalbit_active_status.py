"""Read-only compact status for I05 and the larger native trace collector."""
import pathlib,json,subprocess,shutil
out=pathlib.Path('/kaggle/working/hp_round7');r={}
for name in ['bit_placement_residual_pilot_v1','lex_finalbit_2m_v1']:
    d=out/name;log=out/(name+'_controller.log')
    r[name]={'log_tail':log.read_text()[-1500:] if log.is_file() else None}
    for n in ['summary.json','manifest.json','results.json']:
        p=d/n
        if p.is_file():r[name][n]=json.loads(p.read_text())
    if name=='lex_finalbit_2m_v1':r[name]['trace_file_bytes']={n:(d/n/'final_p.u16').stat().st_size if (d/n/'final_p.u16').is_file() else None for n in 'abcd'}
r['active']='\n'.join(s for s in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'lex_finalbit_2m_worker.py' in s or 'bit_placement_residual.py' in s or '/cmix_trace' in s)
r['persistent_free_bytes']=shutil.disk_usage('/kaggle/working').free
print(json.dumps(r,indent=2))
