import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'error_memory_preflight_v1';D.mkdir(exist_ok=False)
p=subprocess.run(['g++','-O3','-march=x86-64-v3','-mrecip=none','-std=c++17',str(R/'research_round8_error_memory.cpp'),'-o',str(D/'replay')],capture_output=True,text=True);(D/'compile.log').write_text(p.stdout+p.stderr)
if p.returncode:print(json.dumps({'status':'COMPILE_FAIL','tail':p.stderr[-2600:]}))
else:
 p=subprocess.run([str(D/'replay'),'selftest'],capture_output=True,text=True);(D/'selftest.log').write_text(p.stdout+p.stderr);print(json.dumps({'status':'PASS' if not p.returncode else 'SELFTEST_FAIL','output':p.stdout+p.stderr}))
