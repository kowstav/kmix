import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7')
for n in ['lex_native_2m_controller.log','lex_native_2m_decode_controller.log']:
    p=out/n
    if p.exists():print(n,p.read_text()[-700:])
for n in ['c','d','a','b']:
    p=out/'lex_native_2m'/(n+'.log')
    if p.exists():print('NATIVE2M',n,p.read_text()[-120:])
print('RUNNING','\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'cmix_round7_lex_codebook ' in x))
print('DISK',subprocess.check_output(['df','-B1','/kaggle/working'],text=True).splitlines()[-1])
