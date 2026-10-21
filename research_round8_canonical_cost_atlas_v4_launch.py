import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'canonical_cost_atlas_v4').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_canonical_cost_atlas_v4.py')],stdout=(R/'canonical_cost_atlas_v4_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'canonical_cost_atlas_v4','reason':'check ideal regret using independent batch normalizer, report per-step accumulation roundoff explicitly','spending_usd':0,'deletions':[]}))

