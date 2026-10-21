"""Isolated minimal runtime and strict checkpoint shape contracts; no forward/SGD."""
import pathlib,subprocess,sys,tarfile,hashlib,json,time,gc,traceback
out=pathlib.Path('/kaggle/working/hp_round7');site=pathlib.Path('/root/hp/round7_runtime_site');site.mkdir(exist_ok=False)
packages=pathlib.Path('/root/hp/round7_runtime_packages')
selected=['fla_core-0.5.1-py3-none-any.whl','jaxtyping-0.3.11-py3-none-any.whl','wadler_lindig-0.1.3-py3-none-any.whl']
install=subprocess.run(['python','-m','pip','install','--no-deps','--no-index','--target',str(site),*[str(packages/n) for n in selected]],timeout=120)
assert install.returncode==0,'Minimal isolated runtime installation failed'
sys.path.insert(0,str(site))
repo=pathlib.Path('/root/hp/src/fx2-cmix-transformer-v1');repo.mkdir(parents=True,exist_ok=False)
tools=pathlib.Path('/root/hp/tools');tools.mkdir(exist_ok=False)
prefix='src/fx2-cmix-transformer-v1/'
names=['6m-q4-fp32.tch','8m.tch','10m.tch']
expected={'6m-q4-fp32.tch':'2ca3428f729799a93927822c14c67ef99493ceeabf6e82895b7f07646b4024fd',
          '8m.tch':'a88aad29b44fc58bb5e1a9d0f4123d34e58a1d2945e7067566030158965cdbbb',
          '10m.tch':'c84a6d4cfcb9915d38b9447d95290815007cb85c5fdc28cd4d39c642155fb7a7'}
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for m in tar.getmembers():
        if not m.isfile() or not m.name.startswith(prefix):continue
        suffix=m.name[len(prefix):]
        if not (suffix.startswith('pysrc/') and suffix.endswith('.py') or suffix in ['models/'+n for n in names]):continue
        target=repo/suffix;assert target.resolve().is_relative_to(repo.resolve());target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(tar.extractfile(m).read())
    (tools/'tfh.py').write_bytes(tar.extractfile('tools/tfh.py').read())
sys.path.insert(0,str(tools));sys.path.insert(0,str(repo))
rows=[];result={'scope':'Strict structural checkpoint load only; no logits, probability comparison, training, paid rental or deletion',
              'site':str(site),'global_torch_unchanged':True,'restored_original_sources':True,'models':rows}
try:
    import torch,tfh
    torch.set_num_threads(1)
    for name in names:
        p=repo/'models'/name;digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==expected[name]
        sd=torch.load(p,map_location='cpu',weights_only=True)
        if all(k.startswith('_orig_mod.') for k in sd):sd={k[len('_orig_mod.'):]:v for k,v in sd.items()}
        nl=1+max(int(k.split('.')[1]) for k in sd if k.startswith('blocks.'))
        d=sd['embedding.weight'].shape[1]
        overrides=dict(n_layers=nl,attention_weight_sharing_pattern=list(range(nl)),mlp_weight_sharing_pattern=list(range(nl)),
                       d_model=d,d_mlp=d*4,n_query_heads=d//64,n_key_value_heads=d//64,kimi_linear_n_heads=d//64,
                       kimi_linear=[True,True,True,False]*(nl//4))
        row={'checkpoint':name,'sha256':digest,'derived_layers':nl,'derived_width':d,
             'assumptions':'Remaining configuration inherited from known6M recipe; strict shapes do not validate unstored hyperparameters'}
        try:
            model=tfh.Transformer(tfh.make_config(quantized=name=='6m-q4-fp32.tch',**overrides))
            model.load_state_dict(sd,strict=True);model.eval();row.update(strict_structure_load=True,keys=len(sd),tensor_elements=sum(v.numel() for v in sd.values()))
            del model
        except Exception as e:row.update(strict_structure_load=False,error=str(e),traceback=traceback.format_exc())
        rows.append(row);del sd;gc.collect();print(json.dumps(row),flush=True)
except Exception as e:
    result.update(runtime_import_succeeded=False,error=str(e),traceback=traceback.format_exc());print(result['traceback'],flush=True)
else:result['runtime_import_succeeded']=True
(out/'frozen_shape_probe_results.json').write_text(json.dumps(result,indent=2))
print('FROZEN_SHAPE_PROBE_COMPLETE',flush=True)
