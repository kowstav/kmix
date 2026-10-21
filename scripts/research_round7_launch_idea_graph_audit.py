import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_idea_arch_graph_audit.py'
assert script.is_file() and not (out/'idea_arch_graph_audit_v1').exists(),'Preserve evidence; do not duplicate'
assert not any(str(script) in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()),'Audit already active'
with (out/'idea_arch_graph_audit_v1_controller.log').open('x') as log:
    p=subprocess.Popen(['python3','-u',str(script)],cwd=out,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_pid':p.pid,'job':'I01 dictionary-only bounded-neighbor recall audit','paid_rental_usd':0,'deletions':[]}))
