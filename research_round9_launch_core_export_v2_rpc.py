import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'core_export_v2').exists();assert json.loads((R/'core_export_v1/manifest.json').read_text())['status']=='FAIL'
p=subprocess.Popen(['python3',str(R/'research_round9_core_export_v2_worker.py')],stdout=(R/'core_export_v2.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'scope':'reuse actual trained exports; compact rope regeneration and native decoder CLI repair'}))
