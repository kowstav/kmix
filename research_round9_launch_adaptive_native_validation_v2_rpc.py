import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'adaptive_native_v2').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_adaptive_native_validation_v2_worker.py')],stdout=(R/'adaptive_native_v2.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'scope':'reuse unchanged G candidate and validate corrected reference; new H exact encode/decode'}))
