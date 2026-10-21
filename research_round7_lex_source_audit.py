import pathlib, tarfile, json, hashlib
out=pathlib.Path('/kaggle/working/hp_round7'); dest=out/'lex_audit';dest.mkdir(exist_ok=True)
names=['README.md','build.sh','makefile','cpp_infer/src/weights_io_compressed.cpp','cpp_infer/include/weights_io.h','src/runner.cpp','evidence/lexth11c/lex_build_lexth11c.json','docs/HUTTER_WRITEUP.md']
prefix='src/cmix-lex-transformer/'
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for name in names:
        full=prefix+name
        try:m=tar.getmember(full)
        except KeyError:print('MISSING',name);continue
        b=tar.extractfile(m).read();p=dest/name.replace('/','__');p.write_bytes(b)
        print('SAVED',name,len(b),hashlib.sha256(b).hexdigest())
        if name in ['build.sh','evidence/lexth11c/lex_build_lexth11c.json']:print(b.decode('utf8',errors='replace')[:8000])
        if name=='src/runner.cpp':print('RUNNER_LAB_LINES',[(i+1,x.strip()) for i,x in enumerate(b.decode().splitlines()) if 'LAB_' in x or 'Usage:' in x])
        if 'weights_io' in name:print('FORMAT_LINES',[(i+1,x.strip()) for i,x in enumerate(b.decode().splitlines()) if 'FX2' in x or 'codebook' in x or 'version' in x])
    m=tar.getmember(prefix+'models/lex_h1_run11.tfwc2');b=tar.extractfile(m).read();(dest/'lex_h1_run11.tfwc2').write_bytes(b)
    print('LEX_MODEL',len(b),b[:8].decode('ascii'),hashlib.sha256(b).hexdigest())
