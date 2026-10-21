import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');assert not (out/'lex_native_2m_controller.log').exists()
with (out/'lex_native_2m_controller.log').open('w') as f:p=subprocess.Popen(['python','-u',str(out/'research_round7_lex_2m_controller.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'lex_larger_validation_controller_pid':p.pid,'order':'C/D then A/B','input_bytes_per_slice':2000000,'maximum_native_jobs':2,'prefix_cost_parity_required':True,'existing_successful_controls_reused':True}))
