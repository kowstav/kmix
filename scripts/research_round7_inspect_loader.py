import pathlib,json
base=pathlib.Path('/root/hp/round7_lab')
for name in ['cpp_infer/src/weights_io.cpp','cpp_infer/src/test_weights_compressed.cpp','cpp_infer/src/weights_io.h']:
    p=base/name;print(name,p.read_text()[:13000])
print('CANDIDATE_TREE',[str(p) for p in pathlib.Path('/root/hp/cand_final2').iterdir()])
print('BUILD_SCRIPTS',[str(p) for p in pathlib.Path('/root/hp/src/cmix-lex').glob('*sh')])
print('CODEC_LOG',(pathlib.Path('/kaggle/working/hp_round7/v5_codec.log').read_text())[-1200:])
