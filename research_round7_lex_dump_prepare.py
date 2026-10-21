import pathlib,tarfile,subprocess,shutil,os,json
out=pathlib.Path('/kaggle/working/hp_round7');dest=pathlib.Path('/root/hp/lex_codec_lab')
dest.mkdir(exist_ok=False)
names=['cpp_infer/src/weights_io.cpp','cpp_infer/src/weights_io.h','cpp_infer/src/weights_io_compressed.cpp']
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for name in names:
        b=tar.extractfile('src/cmix-lex-transformer/'+name).read()
        (dest/pathlib.PurePosixPath(name).name).write_bytes(b)
print('COMPILERS',{x:shutil.which(x) for x in ['clang++-17','clang++','clang++-20','g++']})
src=(dest/'weights_io_compressed.cpp').read_text()
assert src.count('wf.promote_small_bf16_to_f32();')==2
(dest/'weights_io_compressed_unpromoted.cpp').write_text(src.replace('wf.promote_small_bf16_to_f32();','// Keep the original serialized dtype for format analysis.'))
dump=out/'research_round7_tensor_dump.cpp'
assert dump.exists()
compiler=shutil.which('clang++') or shutil.which('g++')
assert compiler
subprocess.run([compiler,'-std=c++17','-O2','-I'+str(dest),str(dump),str(dest/'weights_io.cpp'),str(dest/'weights_io_compressed_unpromoted.cpp'),'-o',str(out/'lex_tensor_dump_unpromoted')],check=True)
subprocess.run([str(out/'lex_tensor_dump_unpromoted'),str(out/'lex_audit/lex_h1_run11.tfwc2'),str(out/'lex_audit/lex_unpromoted_raw.bin')],check=True)
print('LEX_DUMP_COMPLETE',json.dumps({'raw_bytes':(out/'lex_audit/lex_unpromoted_raw.bin').stat().st_size,'no_neural_training':True}))
