import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7')
assert not (out/'runtime_package_audit.log').exists(),'Refuse duplicate package audit'
with (out/'runtime_package_audit.log').open('w') as f:
    p=subprocess.Popen(['python','-u',str(out/'research_round7_runtime_package_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'package_audit_pid':p.pid,'no_installation':True,'no_training':True}))
