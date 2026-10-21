"""Compact read-only status for current placement and final-bit trace jobs."""
import json,pathlib,subprocess
out=pathlib.Path('/kaggle/working/hp_round7');r={}
for n in ['idea_arch_directed_lag_v1','lex_finalbit_trace_v2','placement_pair_audit_v1']:
    d=out/n;p=d/('summary.json' if 'directed' in n or 'pair_audit' in n else 'results.json');log=out/(n+'_controller.log')
    r[n]={'result':json.loads(p.read_text()) if p.is_file() else None,'log_tail':log.read_text()[-1700:] if log.is_file() else None}
r['active']='\n'.join(s for s in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'directed_lag_screen.py' in s or 'lex_finalbit_trace_finish.py' in s or 'placement_pair_audit.py' in s or '/cmix_trace' in s)
print(json.dumps(r,indent=2))
