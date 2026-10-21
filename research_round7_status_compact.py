import pathlib,json,subprocess
out=pathlib.Path('/kaggle/working/hp_round7')
for name in ['lex_native_v3_controller.log']:
    p=out/name
    if p.exists():print(name,p.read_text()[-700:])
print('ACTIVE','\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if any(v in x for v in ['cmix_round7_lex','lex_exact_build_worker.py','topic_selector_screen.py','clang++-17'])))
dest=out/'lex_native_v3'
if dest.exists():
    for p in sorted(dest.glob('*.log')):print(p.name,p.read_text()[-180:])
