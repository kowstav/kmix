def _hp_round7_read_code():
    import pathlib, json
    files=['/root/hp/lexFM/src/preprocess/dictionary.cpp','/root/hp/lexFM/src/preprocess/preprocessor.cpp','/root/hp/lexFM/src/predictor.cpp','/root/hp/lexFM/src/coder/encoder.cpp','/root/hp/lexFM/src/readalike_prepr/phda9_preprocess.h','/root/hp/tools/structx.h','/root/hp/tools/sxpatch.py']
    print(json.dumps({'files':{n:pathlib.Path(n).read_text() for n in files},'lists':{}}))
_hp_round7_read_code()
del _hp_round7_read_code
