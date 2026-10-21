"""Read-only runtime compatibility inventory; no installations or model execution."""
import json,pathlib,sys,importlib.metadata,subprocess,tarfile,hashlib
import torch
out=pathlib.Path('/kaggle/working/hp_round7')
versions={}
for n in ['torch','triton','flash-linear-attention','flash-attn','jaxtyping','causal-conv1d','beartype','numpy']:
    try:versions[n]=importlib.metadata.version(n)
    except importlib.metadata.PackageNotFoundError:versions[n]=None
result={'python':sys.version,'packages':versions,'torch_cuda':torch.version.cuda,
        'gpus':[{'name':torch.cuda.get_device_name(i),'compute_capability':list(torch.cuda.get_device_capability(i))} for i in range(torch.cuda.device_count())],
        'current_device_native_bfloat16_support':torch.cuda.is_bf16_supported(including_emulation=False),
        'scope':'Compatibility inventory only, no network/package installation, GPU inference, SGD or paid rental'}
selected={}
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for name in ['tools/tfh.py','src/cmix-lex-transformer/src/predictor.cpp','src/fx2-cmix-transformer-v1/pysrc/data.py']:
        try:m=tar.getmember(name)
        except KeyError:continue
        b=tar.extractfile(m).read();selected[name]={'sha256':hashlib.sha256(b).hexdigest(),'text':b.decode('utf-8','replace')}
result['selected_source_contracts']=selected
(out/'runtime_readiness.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='selected_source_contracts'}));print('CONTRACT_FILES',list(selected))
