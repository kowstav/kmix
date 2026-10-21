import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7');assert not (out/'frozen_shape_probe.log').exists(),'Refuse duplicate probe'
with (out/'frozen_shape_probe.log').open('w') as f:
    p=subprocess.Popen(['python','-u',str(out/'research_round7_frozen_shape_probe_worker.py')],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'frozen_structure_probe_pid':p.pid,'no_forward':True,'no_training':True,'no_global_torch_upgrade':True}))
