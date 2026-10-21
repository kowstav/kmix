import pathlib,subprocess,json,py_compile
R=pathlib.Path('/kaggle/working/hp_round10');out=[]
for name,worker in [('preflight_v3','research_round10_preflight_worker.py'),('warm_atlas_v1','research_round10_warm_atlas_worker.py')]:
 p=R/worker;py_compile.compile(str(p),doraise=True);assert not (R/name).exists()
 child=subprocess.Popen(['python3',str(p)],stdout=(R/(name+'.log')).open('x'),stderr=subprocess.STDOUT,start_new_session=True)
 out.append({'job':name,'pid':child.pid,'GPU':False})
print(json.dumps(out))
