import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'residual_throughput_v1').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_residual_throughput_worker.py')],stdout=(R/'residual_throughput_v1_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'residual_throughput_v1','paid_spending_usd':0,'deletions':[]}))
