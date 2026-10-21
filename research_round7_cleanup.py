def _hp_round7_cleanup():
    import os, json, pathlib, shutil, datetime
    root=pathlib.Path('/kaggle/working/hutter_lab/exp4').resolve()
    out=pathlib.Path('/kaggle/working/hp_round7'); out.mkdir(exist_ok=True)
    names=['pmix_tok_dtok_distrib_ce_long2_ext.npy','pmix_e2.npy','pmix_e3.npy','pmix_tok_dtok_distrib_ce_long3_r.npy','pmix_tok_dtok_distrib_ce_long4_r.npy','pmix_tok_dtok_distrib_ce_long_big.npy']
    plan=[]
    for name in names:
        path=root/name
        if path.is_symlink() or path.resolve().parent != root: raise RuntimeError('Unexpected cleanup target')
        if not path.exists(): continue
        if not path.is_file(): raise RuntimeError('Cleanup target is not a regular file')
        st=path.stat()
        plan.append({'path':str(path),'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'reason':'Regenerable dense enwik8 probability matrix from prior round4 experiments. Preserve scripts, model checkpoints, result metrics and all enwik9 assets.'})
    targets={v['path'] for v in plan}
    open_files=[]
    for proc in pathlib.Path('/proc').iterdir():
        if not proc.name.isdigit(): continue
        try:
            for fd in (proc/'fd').iterdir():
                try:
                    target=os.readlink(fd)
                    if target in targets: open_files.append({'pid':proc.name,'file':target})
                except OSError: pass
        except OSError: pass
    if open_files: raise RuntimeError('Selected outputs are in use: '+json.dumps(open_files))
    ledger=out/'deletion_manifest.jsonl'
    before=shutil.disk_usage('/kaggle/working').free
    with ledger.open('a') as log:
        for item in plan:
            record={**item,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'planned'}
            log.write(json.dumps(record)+'\n'); log.flush(); os.fsync(log.fileno())
            pathlib.Path(item['path']).unlink()
            record['status']='deleted'
            log.write(json.dumps(record)+'\n'); log.flush(); os.fsync(log.fileno())
    print(json.dumps({'deleted':plan,'free_before':before,'free_after':shutil.disk_usage('/kaggle/working').free,'manifest':str(ledger)}))
_hp_round7_cleanup()
del _hp_round7_cleanup
