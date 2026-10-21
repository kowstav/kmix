import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'adaptive_strict_v1').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_adaptive_strict_worker.py')],stdout=(R/'adaptive_strict_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'scope':'strict-FP standalone replay; reuses G teacher'}))
