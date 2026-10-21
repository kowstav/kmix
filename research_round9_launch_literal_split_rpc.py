import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'literal_split_v1').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_literal_split_worker.py')],stdout=(R/'literal_split_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid,'scope':'priced rare-literal redaction under actual combined native CM'}))
