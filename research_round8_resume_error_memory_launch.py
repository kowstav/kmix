import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'error_memory_resume_v1').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_resume_error_memory_worker.py')],stdout=(R/'error_memory_resume_v1_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'error_memory_resume_v1','parent':'atom_fit_resume_v1','preserved_native_exports_reused':True,'spending_usd':0,'deletions':[]}))
