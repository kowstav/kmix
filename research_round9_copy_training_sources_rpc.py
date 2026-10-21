import pathlib,json,shutil
src=pathlib.Path('/root/hp_round9/restored/src/fx2-cmix-transformer-v1/pysrc');out=pathlib.Path('/kaggle/working/hp_round9/recovered_training_sources');out.mkdir(exist_ok=True)
for name in ['model.py','quantization.py','export_weights.py','weights_compress.py','kda_reference.py']:
 p=out/name
 if not p.exists():shutil.copyfile(src/name,p)
print(json.dumps({'files':[p.name for p in out.iterdir()]}))
