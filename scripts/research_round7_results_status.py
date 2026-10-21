def _hp_results_status():
    import pathlib,json,subprocess,shutil
    out=pathlib.Path('/kaggle/working/hp_round7');r={'free_disk':shutil.disk_usage(out).free,'results':{}}
    for p in sorted(out.glob('*.json')):
        if not any(x in p.name for x in ['screen','temperature','trace','word_context']):continue
        try:o=json.loads(p.read_text())
        except ValueError:continue
        s={k:o[k] for k in ['baseline_ideal_bytes','baseline_bits_per_symbol','memory','memory_keys','accounted_memory_payload_bytes','maximum_absolute_error_bits','old_cost_difference_ideal_bytes','trace_cost_vs_dump_bits'] if k in o}
        if 'scores' in o:s['gains']={k:v['prequential_saving_bytes'] for k,v in o['scores'].items()}
        if 'score' in o:s['score']={k:o['score'][k] for k in ['events','prequential_saving_bytes','oracle_best_per_event_saving_bytes_UNPAID'] if k in o['score']}
        if 'policies' in o:s['policies']=o['policies']
        if 'prequential_mixtures' in o:s['mixtures']=o['prequential_mixtures'];s['best_fixed']=max(o['fixed_temperatures'],key=lambda v:v['saving_bytes'])
        if 'categories' in o:s['budgets']={k:v['share_total_bits'] for k,v in o['categories'].items() if 'hard_word' not in k and 'previous_word' not in k}
        r['results'][p.name]=s
    logs=['confirmation_controller.log','trace_controller.log','build_sx_control.log','a_native_edit.log','b_native_edit.log','a_line.log','b_line.log','word_context_atlas.log']
    r['logs']={name:(out/name).read_text(errors='replace')[-900:] for name in logs if (out/name).exists()}
    r['processes']=subprocess.check_output(['ps','-eo','pid,ppid,etime,%cpu,rss,comm','--sort=-%cpu'],text=True).splitlines()[:13]
    print(json.dumps(r))
_hp_results_status()
del _hp_results_status
