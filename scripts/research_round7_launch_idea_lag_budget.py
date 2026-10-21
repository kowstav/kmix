import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_idea_arch_lag_budget.py'
assert script.is_file() and not (out/'idea_arch_lag_budget_v1').exists(),'Evidence exists; do not duplicate'
assert not any(str(script) in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()),'Diagnostic already active'
log=(out/'idea_arch_lag_budget_v1_controller.log').open('x')
p=subprocess.Popen(['python3','-u',str(script)],cwd=out,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
log.close();print(json.dumps({'started_pid':p.pid,'job':'I02 restricted lag-neighbor residual budget; not achieved compression','deletions':[],'paid_rental_usd':0}))
