import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'atom_cache_preflight_v1';D.mkdir(exist_ok=False)
cmd=['g++','-O3','-march=x86-64-v3','-mrecip=none','-std=c++17',str(R/'research_round8_atom_cache.cpp'),'-o',str(D/'replay')]
p=subprocess.run(cmd,capture_output=True,text=True);(D/'compile.log').write_text(p.stdout+p.stderr)
if p.returncode:print(json.dumps({'status':'COMPILE_FAIL','tail':p.stderr[-2200:]}))
else:
 p=subprocess.run([str(D/'replay'),'selftest',str(R/'native_hidden_trace_v1/tree/dictionary/english.dic')],capture_output=True,text=True);(D/'selftest.log').write_text(p.stdout+p.stderr);print(json.dumps({'status':'PASS' if not p.returncode else 'SELFTEST_FAIL','output':p.stdout+p.stderr}))
