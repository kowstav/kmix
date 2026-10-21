import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'semantic_replay_v1';graph=R/'semantic_graph_v1/manifest.json'
g=json.loads(graph.read_text());assert g['status']=='COMPLETE_GRAPH_NOT_COMPRESSION_RESULT',g['status']
if D.exists():print(json.dumps({'reused':True,'manifest':json.loads((D/'manifest.json').read_text())}))
else:
 with (R/'semantic_replay_v1_controller.log').open('x') as log:p=subprocess.Popen(['python',str(R/'research_round8_semantic_replay_worker.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps({'launched':True,'pid':p.pid,'path':str(D)}))
