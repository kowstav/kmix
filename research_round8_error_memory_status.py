import pathlib,json
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'error_memory_v1';p=D/'manifest.json'
if not p.exists():print(json.dumps({'status':'NO_MANIFEST'}))
else:
 m=json.loads(p.read_text());print(json.dumps({k:m.get(k) for k in ['status','stage','pid','error','feature_exports','best_priced_AB_bytes','fixed_online_AB','advance_gate_pass','confirmation_candidates_evaluated','results']}));print(json.dumps({'controller_tail':(R/'error_memory_v1_controller.log').read_text()[-1600:]}))
