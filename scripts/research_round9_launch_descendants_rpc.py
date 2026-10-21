import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');out=[]
assert json.loads((R/'word_softmax_v1/manifest.json').read_text())['status'].startswith('COMPLETE')
for name,file in [('distributed_core_data_v1','research_round9_distributed_core_data_worker.py'),('word_softmax_v2','research_round9_word_softmax_v2_worker.py')]:
 assert not (R/name).exists(),('reuse existing manifest',name)
 p=subprocess.Popen(['python3',str(R/file)],stdout=(R/(name+'.log')).open('w'),stderr=subprocess.STDOUT,start_new_session=True);out.append({'job':name,'pid':p.pid})
print(json.dumps(out))
