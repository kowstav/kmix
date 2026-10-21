import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'known_literals_v1').exists();assert json.loads((R/'literal_split_v1/manifest.json').read_text())['status'].startswith('COMPLETE')
p=subprocess.Popen(['python3',str(R/'research_round9_known_literals_worker.py')],stdout=(R/'known_literals_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'scope':'no double coding of constants; native context and trained-common specialist comparison'}))
