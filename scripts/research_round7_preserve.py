def _hp_round7_preserve():
    import pathlib, subprocess, json, os
    out=pathlib.Path('/kaggle/working/hp_round7')
    code="""
import pathlib, shutil, tarfile, json, hashlib
out=pathlib.Path('/kaggle/working/hp_round7'); dest=out/'preserved'; dest.mkdir(exist_ok=True)
paths=['/root/hp/data/enwik9.zip','/root/hp/data/vocab.bm','/root/hp/data/vocab.list','/root/hp/data/bounds.i32','/root/hp/gen/.dict','/root/hp/gen/.new_article_order','/root/hp/slices/a2m.bin','/root/hp/slices/b2m.bin','/root/hp/slices/a2m.probs.f16','/root/hp/slices/b2m.probs.f16','/root/hp/runs/lex_a/cost.f32','/root/hp/runs/lex_b/cost.f32']
manifest=[]
for name in paths:
    src=pathlib.Path(name); rel=src.relative_to('/root/hp'); target=dest/rel
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,target)
    manifest.append({'source':name,'preserved':str(target),'bytes':target.stat().st_size})
def filt(info):
    if '/.git/' in '/'+info.name+'/' or info.name.endswith('.git'): return None
    return info
with tarfile.open(dest/'research_sources_and_candidates.tar.gz','w:gz',compresslevel=3) as tar:
    for name in ['/root/hp/tools','/root/hp/src/fx2-cmix-transformer-v1','/root/hp/src/cmix-lex-transformer','/root/hp/cand_final2/src','/root/hp/cand_final2/run','/root/hp/cand_final2/makefile','/root/hp/results']:
        if pathlib.Path(name).exists(): tar.add(name,arcname=str(pathlib.Path(name).relative_to('/root/hp')),filter=filt)
(dest/'preservation_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'preserved_files':len(manifest),'archive_bytes':(dest/'research_sources_and_candidates.tar.gz').stat().st_size,'complete':True}),flush=True)
"""
    script=out/'preserve_worker.py'; script.write_text(code)
    with (out/'preserve.log').open('w') as f:
        process=subprocess.Popen(['python','-u',str(script)],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    (out/'preserve.pid').write_text(str(process.pid))
    print(json.dumps({'pid':process.pid,'log':str(out/'preserve.log')}))
_hp_round7_preserve()
del _hp_round7_preserve
