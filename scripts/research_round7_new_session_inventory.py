import pathlib,subprocess,json,shutil
out=pathlib.Path('/kaggle/working/hp_round7')
print('ROOT_HP_PRESENT',pathlib.Path('/root/hp').exists())
print('PERSISTENT_FILES',[(p.name,p.stat().st_size) for p in out.iterdir() if p.is_file() and (p.suffix in ['.json','.gz'] or 'cmix' in p.name or 'inference' in p.name or 'v5_' in p.name)])
for name in ['v5_package_screen.json','v5_native_inference.json','v5_package_retry.log','v5_inference_controller.log','v5_inference_old.log','v5_inference_v5.log']:
    p=out/name
    if p.exists():print(name,p.read_text()[-1800:])
print('PRESERVED',[(str(p.relative_to(out)),p.stat().st_size) for p in (out/'preserved').glob('*')])
print('DISK',subprocess.check_output(['df','-h','/kaggle/working','/tmp'],text=True))
print('ACTIVE_EXPERIMENTS','\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'cmix ' in x or 'round7_' in x))
print('COMPILER',shutil.which('clang++-17'))
print('GPU',subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.used','--format=csv,noheader'],text=True))
