import pathlib,subprocess,json,py_compile
R=pathlib.Path('/kaggle/working/hp_round10');R.mkdir(exist_ok=True)
p=R/'research_round10_warm_atlas_worker.py';py_compile.compile(str(p),doraise=True)
assert not (R/'warm_atlas_v1').exists(),'Reuse the existing manifest; never launch a duplicate.'
child=subprocess.Popen(['python3',str(p)],stdout=(R/'warm_atlas_v1.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'job':'R10-E0-early-warm-atlas','pid':child.pid,'GPU':False,'paid_usd':0}))
