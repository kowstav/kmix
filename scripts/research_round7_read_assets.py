def _hp_round7_read_assets():
    import json, pathlib
    roots=['/root/hp/tools','/root/hp/data','/root/hp/slices','/root/hp/runs/base_a','/root/hp/runs/base_b','/root/hp/runs/lex_a','/root/hp/dic','/root/hp/lexFM/src','/root/hp/src/cmix-lex-transformer']
    files=['/root/hp/tools/tfh.py','/root/hp/tools/genprobs.py','/root/hp/tools/labpatch.py','/root/hp/tools/slicepipe.py','/root/hp/tools/wstats.py','/root/hp/tools/lt_eval.py','/root/hp/tools/finalmix.py']
    result={'lists':{},'files':{}}
    for name in roots:
        p=pathlib.Path(name)
        if p.is_dir(): result['lists'][name]=[{'name':x.name,'size':x.stat().st_size,'is_dir':x.is_dir()} for x in p.iterdir()]
    for name in files:
        p=pathlib.Path(name)
        if p.is_file(): result['files'][name]=p.read_text()
    print(json.dumps(result))
_hp_round7_read_assets()
del _hp_round7_read_assets
