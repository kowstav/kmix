"""Read-only compact status of current constructor and final-trace jobs."""
import pathlib,json,subprocess,shutil
root=pathlib.Path('/kaggle/working/hp_round7');result={}
for name in ['lex_finalbit_2m_v1','constructor_split_v1','constructor_skeleton_v1']:
    d=root/name;r={};p=d/'manifest.json'
    if p.is_file():r['manifest_status']=json.loads(p.read_text())['status']
    p=d/('results.json' if name=='lex_finalbit_2m_v1' else 'summary.json')
    if p.is_file():
        rows=json.loads(p.read_text())
        if name=='lex_finalbit_2m_v1':r['completed']=[{k:v[k] for k in ['slice','ready_for_residual_screen','trace_bytes','native_archive_bytes','user_seconds','max_rss_kbytes','bit_trace_sha256']} for v in rows]
        else:r['completed']=[{'slice':v['slice'],'saved_bytes':[s['bytes_saved_before_incremental_decoder'] for s in v['screen_rows']]} for v in rows]
    if name=='constructor_skeleton_v1':
        p=root/(name+'_controller.log');r['log_tail']=p.read_text()[-1800:] if p.is_file() else None
    result[name]=r
result['active']='\n'.join(s for s in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'constructor_skeleton.py' in s or 'lex_finalbit_2m_worker.py' in s or '/cmix_trace' in s)
result['persistent_free_bytes']=shutil.disk_usage('/kaggle/working').free
print(json.dumps(result,indent=2))
