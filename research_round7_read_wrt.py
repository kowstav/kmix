def _hp_round7_read_wrt():
    import pathlib, json
    result={'files':{},'lists':{}}
    roots=['/root/hp/lexFM/src/preprocess','/root/hp/lexFM/src/readalike_prepr','/root/hp/lexFM/src/mixer','/root/hp/gen','/root/hp/results']
    for r in roots:
        p=pathlib.Path(r)
        if p.is_dir(): result['lists'][r]=[{'name':x.name,'size':x.stat().st_size} for x in p.iterdir()]
    for r in ['/root/hp/tools/genprobs.py','/root/hp/tools/revan.py','/root/hp/tools/iw_stats.py','/root/hp/tools/labrun.sh','/root/hp/tools/lexpatch.py','/root/hp/lexFM/src/predictor.h','/root/hp/lexFM/makefile']:
        p=pathlib.Path(r)
        if p.is_file(): result['files'][r]=p.read_text()
    result['dictionary_prefix']=pathlib.Path('/root/hp/dic/dic.txt').read_text(errors='replace')[:2000]
    result['stream_prefix_hex']=pathlib.Path('/root/hp/slices/a2m.bin').read_bytes()[:1000].hex()
    print(json.dumps(result))
_hp_round7_read_wrt()
del _hp_round7_read_wrt
