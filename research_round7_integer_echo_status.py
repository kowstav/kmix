"""Compact read-only continuation status for the sole active idea experiment."""
import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7')
for n in ['idea_arch_integer_echo_v1','idea_arch_integer_graph_cpu_v1']:
    p=out/n/('summary.json' if 'echo' in n else 'results.json');log=out/(n+'_controller.log')
    print(n,'RESULT',p.read_text() if p.is_file() else 'PENDING')
    if 'echo' in n:print('LOG',log.read_text()[-1500:] if log.is_file() else 'MISSING')
print('ACTIVE','\n'.join(s for s in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'research_round7_integer_echo_screen.py' in s))
