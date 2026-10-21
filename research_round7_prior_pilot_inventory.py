import pathlib,json,subprocess
out=pathlib.Path('/kaggle/working/hp_round7')
print('BINARIES',[(p.name,p.stat().st_size) for p in out.iterdir() if p.is_file() and ('cmix' in p.name or p.suffix in ['.tfwc2','.fx2tfwc5'])])
for name in ['v5_native_inference.json','v5_native_verification.json','v5_package_screen.json','frozen_shape_probe_results.json']:
    p=out/name;print('EVIDENCE',name,p.read_text()[-2200:] if p.exists() else 'MISSING')
for name in ['lex_native_2m_recovery_controller.log']:
    p=out/name;print(name,p.read_text()[-2000:])
