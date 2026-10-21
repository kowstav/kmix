import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7')
for name in ['idea_arch_screens_v1','idea_arch_integer_echo_v1','idea_arch_lag_budget_v1','idea_arch_graph_audit_v1','idea_arch_integer_graph_v1','idea_arch_integer_graph_cpu_v1']:
    log=out/(name+'_controller.log');p=out/name/('results.json' if 'graph' in name else 'summary.json')
    print(name,'LOG',log.read_text()[-800:] if log.exists() else 'MISSING')
    if not p.exists():print('RESULT','PENDING');continue
    r=json.loads(p.read_text())
    if 'graph' in name:r={k:v for k,v in r.items() if k not in ['query_results','graph','named_examples','examples','collision_examples']}
    print('RESULT',json.dumps(r))
print('ACTIVE','\n'.join(s for s in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'hp_round7' in s or '/cmix_round7_' in s))
