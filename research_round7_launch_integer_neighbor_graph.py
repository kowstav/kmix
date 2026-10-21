import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');script=out/'research_round7_integer_neighbor_graph.py'
assert script.is_file() and (out/'idea_arch_graph_audit_v1/results.json').is_file() and not (out/'idea_arch_integer_graph_v1').exists(),'Read audit and preserve prior graph; do not duplicate'
assert not any(str(script) in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()),'Graph job active'
with (out/'idea_arch_integer_graph_v1_controller.log').open('x') as log:
    p=subprocess.Popen(['python3','-u',str(script)],cwd=out,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_pid':p.pid,'job':'I01b integer-defined exhaustive neighbor graph','paid_rental_usd':0,'deletions':[]}))
