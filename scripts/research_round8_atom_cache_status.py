import pathlib,json
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'atom_cache_v1';p=D/'manifest.json'
if not p.exists():print(json.dumps({'status':'NO_MANIFEST','controller_tail':(R/'atom_cache_v1_controller.log').read_text()[-1600:]}))
else:
 m=json.loads(p.read_text());print(json.dumps({k:m.get(k) for k in ['status','stage','pid','error','native_exports','feature_exports','best_priced_AB_bytes','fixed_online_AB','advance_gate_pass','confirmation_candidates_evaluated','results']}));print(json.dumps({'controller_tail':(R/'atom_cache_v1_controller.log').read_text()[-1800:]}))
