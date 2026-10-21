import pathlib,json
T=pathlib.Path('/kaggle/working/hp_round8/native_hidden_trace_v1/tree');s=(T/'src/runner.cpp').read_text();o={'main_signatures':[l for l in s.splitlines() if 'main(' in l],'decompression_enwik_branch':'\n'.join(s.splitlines()[1015:1089]),'misc':(T/'src/readalike_prepr/misc.h').read_text()[:8000]};print(json.dumps(o))
