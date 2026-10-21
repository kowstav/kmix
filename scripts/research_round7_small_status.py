import pathlib,json,subprocess,shutil
out=pathlib.Path('/kaggle/working/hp_round7')
for name in ['v5_package_retry.log','v5_inference_controller.log','v5_inference_old.log','v5_inference_v5.log']:
    p=out/name
    if p.exists():print(name,p.read_text()[-2400:])
for name in ['v5_package_screen.json','v5_native_inference.json']:
    p=out/name
    if p.exists():print(name,p.read_text())
print('UPX',shutil.which('upx'))
print('SOURCE_ROOT_FILES',[p.name for p in pathlib.Path('/root/hp/src/cmix-lex').iterdir() if p.is_file()])
print('UPX_CANDIDATE_STRINGS','\n'.join(x for x in subprocess.check_output(['strings','/root/hp/cand_final2/run/cmix_orig'],text=True,errors='replace').splitlines() if 'UPX' in x or 'upx' in x)[:1000])
