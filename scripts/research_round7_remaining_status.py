import json,pathlib,subprocess,tarfile
r=pathlib.Path('/kaggle/working/hp_round7');d=r/'remaining_experts_v1'
print(json.dumps({'manifest':json.loads((d/'manifest.json').read_text()) if (d/'manifest.json').exists() else None,
 'complete':[{'slice':x['slice'],'mixture_saving_bytes':x['mixture_saving_bytes'],'cpu':x['user_seconds']} for x in json.loads((d/'results.json').read_text())] if (d/'results.json').exists() else [],
 'log_tail':(r/'remaining_experts_v1_controller.log').read_text()[-2500:] if (r/'remaining_experts_v1_controller.log').exists() else ''}))
with tarfile.open(r/'preserved/research_sources_and_candidates.tar.gz') as t:
 names=[m.name for m in t.getmembers() if m.isfile()]
 report={'large_files':[{'path':str(p),'bytes':p.stat().st_size} for p in pathlib.Path('/kaggle/working').rglob('*') if p.is_file() and p.stat().st_size>200000000],
         'binary_candidates':[n for n in names if '/bin/' in n or '/run/' in n or n.startswith('tools/')],
         'source':{}}
 for name in ['src/fx2-cmix-transformer-v1/make_training_data.sh','tools/genprobs.py','src/cmix-lex-transformer/src/preprocess_roundtrip.cpp','src/cmix-lex-transformer/src/preprocess/preprocessor.h','src/cmix-lex-transformer/src/runner.cpp','src/cmix-lex-transformer/makefile']:
  if name in names:report['source'][name]=t.extractfile(name).read().decode(errors='replace')
 p=r/'session355529591_source_readiness.json';p.write_text(json.dumps(report,indent=2));print(json.dumps({'source_report':str(p),'large_files':report['large_files'],'binary_candidates':report['binary_candidates']}))
