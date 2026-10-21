import pathlib,tarfile
out=pathlib.Path('/kaggle/working/hp_round7')
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    name='src/cmix-lex-transformer/src/coder/encoder.cpp';data=tar.extractfile(name).read();(out/'lex_audit/encoder.cpp').write_bytes(data);print(data.decode())
