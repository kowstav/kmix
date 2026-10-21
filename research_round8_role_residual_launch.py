import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'role_residual_v1').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_role_residual_worker.py')],stdout=(R/'role_residual_v1_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'role_residual_v1','core_retraining':False,'paid_spending_usd':0,'deletions':[]}))
