import pathlib,tarfile,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7')
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for name in ['tools/labpatch.py','src/cmix-lex-transformer/src/models/ppmd.cpp']:
        data=tar.extractfile(name).read();(out/'lex_audit'/name.replace('/','__')).write_bytes(data)
        if 'labpatch' in name:print(data.decode())
print('PTQ_PROGRESS',(out/'ptq_native_controller.log').read_text()[-2200:])
print('LEX_PROGRESS',(out/'lex_codec.log').read_text()[-1900:])
