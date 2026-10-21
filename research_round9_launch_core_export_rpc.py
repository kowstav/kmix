import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'core_export_v1').exists()
j=json.loads((R/'core_extension_v1/manifest.json').read_text())
assert all(any(v['arm']==name and v['seed']==6506 and v['step']==1152 for v in j['rungs']) for name in ['unweighted','cut107_half','cut1392_zero'])
p=subprocess.Popen(['python3',str(R/'research_round9_core_export_worker.py')],stdout=(R/'core_export_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'scope':'native export and actual neural codec tests; no GPU allocation'}))
