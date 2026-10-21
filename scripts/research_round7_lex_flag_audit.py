import pathlib,tarfile
out=pathlib.Path('/kaggle/working/hp_round7')
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for name in ['build_and_construct_comp.sh','cpp_infer/src/opt/qmat.h','cpp_infer/src/opt/arena_build.cpp','cpp_infer/src/opt/qmat_dense.cpp']:
        data=tar.extractfile('src/cmix-lex-transformer/'+name).read().decode()
        print('FLAGS',name)
        for i,line in enumerate(data.splitlines()):
            if 'TF_' in line or 'codebook' in line or '[-7,7]' in line:print(i+1,line)
        (out/'lex_audit'/name.replace('/','__')).write_text(data)
