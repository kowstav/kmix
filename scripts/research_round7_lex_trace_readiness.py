import shutil,json,pathlib
out=pathlib.Path('/kaggle/working/hp_round7')
print(json.dumps({'clang17':shutil.which('clang++-17'),'lld':shutil.which('ld.lld'),'make':shutil.which('make'),'trace_build_exists':pathlib.Path('/root/hp/lex_finalbit_trace_v1').exists(),'trace_result_exists':(out/'lex_finalbit_trace_v1').exists(),'tar_bytes':(out/'preserved/research_sources_and_candidates.tar.gz').stat().st_size}))
