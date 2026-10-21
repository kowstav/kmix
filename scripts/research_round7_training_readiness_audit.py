"""Read-only source/archive audit for exact frozen-model configuration contracts."""
import pathlib,tarfile,json,hashlib,re
out=pathlib.Path('/kaggle/working/hp_round7')
archive=out/'preserved/research_sources_and_candidates.tar.gz'
interesting=[]; snippets=[]
with tarfile.open(archive,'r:gz') as tar:
    members=tar.getmembers()
    for m in members:
        if not m.isfile():continue
        low=m.name.lower()
        if ('training_recipes' in low or any(x in low for x in ['config','preset','genprobs','train_loop','qtrain','train.py','train.sh','requirements','pyproject'])):
            interesting.append({'path':m.name,'bytes':m.size})
            if m.size<180000 and low.endswith(('.py','.sh','.json','.toml','.txt','.md')):
                b=tar.extractfile(m).read(); text=b.decode('utf-8','replace')
                if '8m' in text or '10m' in text or 'TransformerConfig(' in text or low.endswith(('requirements.txt','pyproject.toml')):
                    # Source only; do not execute commands from archived files.
                    snippets.append({'path':m.name,'sha256':hashlib.sha256(b).hexdigest(),'text':text})
    target_names=['tools/genprobs.py','tools/dump_h.py','tools/qtrain.py']
    for name in target_names:
        try:m=tar.getmember(name)
        except KeyError:continue
        if any(x['path']==name for x in snippets):continue
        b=tar.extractfile(m).read();snippets.append({'path':name,'sha256':hashlib.sha256(b).hexdigest(),'text':b.decode('utf-8','replace')})
result={'archive_bytes':archive.stat().st_size,'interesting_source_members':interesting,'source_snippets':snippets,
        'scope':'Source inspection only; no model execution, dependency installation, data generation or training'}
(out/'training_readiness_source_audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'interesting_source_members':interesting,'selected_source_paths':[x['path'] for x in snippets],'result_bytes':(out/'training_readiness_source_audit.json').stat().st_size}))
