import pathlib,json,subprocess
out=pathlib.Path('/kaggle/working/hp_round7')
for name in ['lex_native_2m_recovery_controller.log','lex_residual_atlas.log']:
    p=out/name;print(name,p.read_text()[-1400:] if p.exists() else 'MISSING')
for folder in ['lex_native_2m_recovered','lex_residual_atlas']:
    p=out/folder;print('RESULT_FILES',folder,[(f.name,f.stat().st_size) for f in p.glob('*.json')])
print('NATIVE','\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'cmix_round7_lex_codebook ' in x))
