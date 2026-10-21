import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');out=[]
for name,file in [('core_native_codec_v3','research_round9_core_native_codec_v3_worker.py'),('core_distributed_v1','research_round9_distributed_core_training_worker.py')]:
 assert not (R/name).exists(),('reuse existing manifest',name)
 p=subprocess.Popen(['python3',str(R/file)],stdout=(R/(name+'.log')).open('w'),stderr=subprocess.STDOUT,start_new_session=True);out.append({'job':name,'pid':p.pid})
print(json.dumps(out))
