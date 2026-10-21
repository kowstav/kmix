"""Read-only current-session inventory before any launch or restoration."""
import datetime,json,pathlib,shutil,subprocess
out=pathlib.Path('/kaggle/working/hp_round7')
names=['idea_arch_integer_echo_v1','idea_arch_directed_lag_v1','lex_finalbit_trace_v1']
r={'session':355454655,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'working_exists':out.is_dir(),'active':'\n'.join(s for s in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'hp_round7' in s or '/cmix_round7_' in s),
   'gpu':subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.used','--format=csv,noheader'],text=True),
   'disk':{k:dict(zip(['total','used','free'],shutil.disk_usage(k))) for k in ['/kaggle/working','/root']},
   'compilers':{n:shutil.which(n) for n in ['clang++-17','ld.lld','ld.lld-17','make']},'jobs':{},'files':{}}
for n in names:
    d=out/n;log=out/(n+'_controller.log')
    r['jobs'][n]={'exists':d.exists(),'summary':(d/'summary.json').read_text() if (d/'summary.json').is_file() else None,
                  'results':(d/'results.json').read_text() if (d/'results.json').is_file() else None,
                  'log_tail':log.read_text()[-2000:] if log.is_file() else None}
for n in ['preserved/research_sources_and_candidates.tar.gz','preserved/gen/.dict',
          'cmix_round7_lex_codebook','lex_audit/lex_h1_run11.tfwc2',
          'research_round7_word_association_screen.py','research_round7_field_screen.py','research_round7_wrt.py']:
    p=out/n;r['files'][n]=p.stat().st_size if p.is_file() else None
print(json.dumps(r,indent=2))
