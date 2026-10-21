import pathlib,json,tarfile,subprocess
P=pathlib.Path('/kaggle/working/hp_round7');T=pathlib.Path('/kaggle/working/hp_round8/native_hidden_trace_v1/tree');out={}
with tarfile.open(P/'preserved/research_sources_and_candidates.tar.gz','r:gz') as t:
 out['order_and_lex_assets']=[{'name':m.name,'bytes':m.size} for m in t.getmembers() if m.isfile() and ('cmix-lex-transformer' in m.name) and any(s in m.name.lower() for s in ['order','lex','preprocess','vocab'])][:90]
for name in ['src/runner.cpp','src/r1_reorder_transform.cpp','src/runner.h']:
 p=T/name
 if not p.is_file():continue
 lines=p.read_text(errors='replace').splitlines();hits=[i for i,s in enumerate(lines) if any(v in s.lower() for v in ['r1_', 'lex_', 'bytes_only','bytes-only','order_path'])];selected=sorted({j for i in hits for j in range(max(0,i-2),min(len(lines),i+4))});out[name]=[{'line':i+1,'text':lines[i]} for i in selected]
out['preserved_gen']=[{'name':p.name,'bytes':p.stat().st_size} for p in (P/'preserved/gen').iterdir() if p.is_file()]
print(json.dumps(out))
