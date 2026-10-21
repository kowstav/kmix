import pathlib,json,tarfile,shutil
P=pathlib.Path('/kaggle/working/hp_round7');T=pathlib.Path('/kaggle/working/hp_round8/native_hidden_trace_v1/tree');o={}
with tarfile.open(P/'preserved/research_sources_and_candidates.tar.gz','r:gz') as t:
 prefix='src/cmix-lex-transformer/'
 o['actual_assets']=[{'name':m.name,'bytes':m.size} for m in t.getmembers() if m.isfile() and m.name.startswith(prefix) and any(v in m.name[len(prefix):].lower() for v in ['order','payload_lex','lexth','lex_h1','dict','gen/'])]
o['runner_preprocess_sections']='\n'.join((T/'src/runner.cpp').read_text().splitlines()[1065:1130])
o['runner_wrt_sections']='\n'.join((T/'src/runner.cpp').read_text().splitlines()[769:825])
o['readme_lex']=(T/'README-cmix-lex.md').read_text()
o['r1_constants']='\n'.join((T/'src/r1_reorder_transform.cpp').read_text().splitlines()[:50])
o['full_regen_assets']=[{'name':str(p),'bytes':p.stat().st_size} for p in (P/'full_stream_regen_v2').iterdir() if p.is_file()]
o['free_bytes']=shutil.disk_usage('/kaggle/working').free
print(json.dumps(o))
