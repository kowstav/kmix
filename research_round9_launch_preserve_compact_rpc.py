import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round9');assert not (R/'compact_preservation_v1').exists()
# Only completed word events can be included; never snapshot a changing TSV.
assert json.loads((R/'word_events_v1/manifest.json').read_text())['status']=='COMPLETE_CAUSAL_WHOLE_WORD_EVENTS'
p=subprocess.Popen(['python3',str(R/'research_round9_preserve_compact_worker.py')],stdout=(R/'compact_preservation_v1.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(json.dumps({'pid':p.pid}))
