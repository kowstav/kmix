"""Read-only inventory after session change; no launches or deletions."""
import pathlib, json, subprocess, shutil, os
out=pathlib.Path('/kaggle/working/hp_round7')
for name in ['lex_native_2m/results.json','lex_native_2m_decode/results.json',
             'lex_native_2m_decode_controller.log','lex_codebook_build_results.json']:
    p=out/name
    print('EVIDENCE',name,p.read_text()[-10000:] if p.exists() else 'MISSING')
for folder in ['lex_native_2m','lex_native_2m_decode','lex_audit']:
    p=out/folder
    print('FILES',folder,[(f.name,f.stat().st_size) for f in p.iterdir() if f.is_file()] if p.exists() else [])
print('EPHEMERAL',[(name,pathlib.Path(name).exists()) for name in ['/root/hp','/root/hp/lex_native_2m','/root/hp/lex_codebook_lab']])
print('TOOLS', {n:shutil.which(n) for n in ['time','clang++-17','g++','zstd','python']})
print('RESOURCES',subprocess.check_output(['free','-b'],text=True),subprocess.check_output(['df','-B1','/kaggle/working','/tmp'],text=True))
print('PROCESSES','\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'cmix' in x or 'round7_' in x))
print('GPU',subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.used','--format=csv,noheader'],text=True))
print('CPU',os.cpu_count())
