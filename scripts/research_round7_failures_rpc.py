import pathlib,tarfile,json
r=pathlib.Path('/kaggle/working/hp_round7')
print((r/'numeric_programs_v1_controller.log').read_text()[:4200])
with tarfile.open(r/'preserved/research_sources_and_candidates.tar.gz') as t:
 found={}
 for n in ['src/fx2-cmix-transformer-v1/src/runner.cpp','cand_final2/src/runner.cpp','src/cmix-lex-transformer/src/preprocess/preprocessor.cpp','src/cmix-lex-transformer/src/preprocess/dictionary.cpp','src/fx2-cmix-transformer-v1/src/preprocess/preprocessor.cpp']:
  try:
   text=t.extractfile(n).read().decode();found[n]=text
  except KeyError:pass
 (r/'session355529591_preprocess_sources.json').write_text(json.dumps(found))
 print(json.dumps({'source_flags':{k:{'prepare_hook':'FX_PREPARE_ONLY' in v,'bytes_only':'bytes_only' in v,'bytes':len(v)} for k,v in found.items()}}))
