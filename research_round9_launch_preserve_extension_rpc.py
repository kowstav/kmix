import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'compact_preservation_v2').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_preserve_extension_worker.py')],stdout=(R/'compact_preservation_v2.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'job':'compact_preservation_v2','pid':p.pid,'root_archive_working_symlink_no_duplicate_bytes':True}))
