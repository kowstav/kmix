def _hp_compact_status():
    import pathlib,json,subprocess,shutil
    out=pathlib.Path('/kaggle/working/hp_round7')
    names=['confirmation_controller.log','a_edit.log','b_edit.log']
    r={'logs':{n:(out/n).read_text(errors='replace')[-1800:] if (out/n).exists() else None for n in names},'free_disk':shutil.disk_usage(out).free}
    for n in ['baseline_validation.json','a_balanced_screen.json','b_balanced_screen.json','a_edit_screen.json','b_edit_screen.json']:
        p=out/n
        if p.exists():
            obj=json.loads(p.read_text())
            r[n]={k:obj[k] for k in ['parser_counts','memory'] if k in obj}
            r[n]['gains']={k:v['prequential_saving_bytes'] for k,v in obj.get('scores',{}).items()}
            if 'bytes' in obj:r[n]=obj
    r['processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,rss,comm','--sort=-%cpu'],text=True).splitlines()[:15]
    for n in ['baseline_c','baseline_d','baseline_validation']:
        p=out/n
        r[n]={f.name:f.stat().st_size for f in p.iterdir() if f.is_file()} if p.exists() else None
        if (p/'run.log').exists():r[n]['log_tail']=(p/'run.log').read_text(errors='replace')[-700:]
    print(json.dumps(r))
_hp_compact_status()
del _hp_compact_status
