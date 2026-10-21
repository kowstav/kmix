import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'compact_download_parts_v2').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_chunk_extension_worker.py')],stdout=(R/'compact_download_parts_v2.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'job':'compact_download_parts_v2','pid':p.pid}))
