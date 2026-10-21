import pathlib,tarfile,hashlib,json,subprocess
out=pathlib.Path('/kaggle/working/hp_round7');dest=pathlib.Path('/root/hp/frozen_checkpoint_audit');dest.mkdir(exist_ok=False)
names=['pysrc/model.py','pysrc/train.py','pysrc/export_weights.py','models/6m-q4-fp32.tch','models/8m.tch','models/10m.tch','models/6m-q4.tch']
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for n in names:
        m=tar.getmember('src/fx2-cmix-transformer-v1/'+n);b=tar.extractfile(m).read();target=dest/n;target.parent.mkdir(exist_ok=True);target.write_bytes(b)
        if n.endswith('.py'):(out/'lex_audit'/('original_'+pathlib.PurePosixPath(n).name)).write_bytes(b)
import torch
rows=[]
for n in names:
    if not n.endswith('.tch'):continue
    data=torch.load(dest/n,map_location='cpu',weights_only=True)
    assert isinstance(data,dict)
    tensors={k:v for k,v in data.items() if isinstance(v,torch.Tensor)}
    row={'name':n,'file_bytes':(dest/n).stat().st_size,'sha256':hashlib.sha256((dest/n).read_bytes()).hexdigest(),'keys':len(data),'tensor_elements':sum(x.numel() for x in tensors.values()),'config_keys':{k:str(v)[:400] for k,v in data.items() if not isinstance(v,torch.Tensor)},'architectural_shapes':{k:list(v.shape) for k,v in tensors.items() if any(x in k for x in ['embedding','blocks.0.','blocks.11.','blocks.15.','blocks.23.'])}}
    rows.append(row);print(json.dumps({k:v for k,v in row.items() if k!='architectural_shapes'}),flush=True)
(out/'checkpoint_shape_audit.json').write_text(json.dumps(rows,indent=2))
print('NATIVE', (out/'lex_native_v3_controller.log').read_text()[-1600:])
print('CHECKPOINT_SHAPE_AUDIT_COMPLETE',flush=True)
