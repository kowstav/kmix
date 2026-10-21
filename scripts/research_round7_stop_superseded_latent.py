import pathlib,os,signal,json,datetime
out=pathlib.Path('/kaggle/working/hp_round7');pid=200;p=pathlib.Path('/proc')/str(pid)/'cmdline'
command=p.read_bytes().replace(b'\0',b' ').decode() if p.exists() else ''
expected='research_round7_causal_latent_word_screen.py'
if expected in command:os.kill(pid,signal.SIGTERM);action='Stopped owned superseded screen'
else:action='Screen already exited or PID no longer belongs to it; no signal sent'
row={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':pid,'action':action,
     'reason':'First expert activation at separator start preceded complete decoded marker; v2 activates only after complete separator',
     'files_deleted':[],'old_sources_logs_results_preserved':True,'native_recovery_untouched':True}
(out/'causal_latent_v1_superseded.json').write_text(json.dumps(row,indent=2));print(json.dumps(row))
