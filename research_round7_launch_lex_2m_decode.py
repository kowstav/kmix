import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');assert not (out/'lex_native_2m_decode_controller.log').exists()
with (out/'lex_native_2m_decode_controller.log').open('w') as f:p=subprocess.Popen(['python','-u',str(out/'research_round7_lex_2m_decode_controller.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'queued_decode_controller_pid':p.pid,'dependency':'existing four2M native compressions must finish successfully','maximum_concurrent_native_jobs':2,'independent_decoder_hashes_required':True}))
