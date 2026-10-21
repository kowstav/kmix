import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9')
assert json.loads((R/'core_distributed_v1/manifest.json').read_text())['status']=='FAIL'
assert not (R/'core_distributed_v2').exists()
p=subprocess.Popen(['python3',str(R/'research_round9_distributed_core_training_v2_worker.py')],stdout=(R/'core_distributed_v2.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'job':'core_distributed_v2','pid':p.pid,'repair':'preserve distributed data manifest across original-core AST setup; prior failure kept'}))
