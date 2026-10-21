import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'canonical_cost_atlas_v1').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_canonical_cost_atlas.py')],stdout=(R/'canonical_cost_atlas_v1_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'canonical_cost_atlas_v1','spending_usd':0,'deletions':[]}))
