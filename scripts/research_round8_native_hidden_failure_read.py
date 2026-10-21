import pathlib,json
D=pathlib.Path('/kaggle/working/hp_round8/native_hidden_trace_v3');m=json.loads((D/'manifest.json').read_text())
print(json.dumps({'failed_runtime':m.get('failed_runtime'),'error':m.get('traceback'),'a_reference_log':(D/'a_reference.log').read_text(errors='replace')[-1200:],'a_hidden_log':(D/'a_hidden.log').read_text(errors='replace')[-1200:],'a_decode_log':(D/'a_decode.log').read_text(errors='replace')[-4000:],'files':{str(p.relative_to(D)):p.stat().st_size for p in D.rglob('*') if p.is_file() and not p.name.endswith('.bin')}}))
