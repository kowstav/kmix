import pathlib,tarfile,json,importlib.util
out=pathlib.Path('/kaggle/working/hp_round7');dest=pathlib.Path('/root/hp/frozen_checkpoint_audit')
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for m in tar:
        if not m.isfile() or not m.name.startswith('src/fx2-cmix-transformer-v1/pysrc/'):continue
        rel=m.name.split('src/fx2-cmix-transformer-v1/',1)[1];p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():p.write_bytes(tar.extractfile(m).read())
        if any(x in rel for x in ['config','utils','quant','dataset']):
            text=p.read_text(errors='replace');print('MODEL_CONFIG_SOURCE',rel,[(i+1,x) for i,x in enumerate(text.splitlines()) if any(s in x for s in ['8m','10m','6m','n_layers','d_model','kimi','prior_embedding','quantization='])][:35])
print('DEPENDENCIES',{n:bool(importlib.util.find_spec(n)) for n in ['torch','fla','triton','jaxtyping','beartype','einops']})
print('MODEL_IMPORTS',(dest/'pysrc/model.py').read_text()[:2600])
print('EXPORT_IMPORTS',(dest/'pysrc/export_weights.py').read_text()[:2100])
