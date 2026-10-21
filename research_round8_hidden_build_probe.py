import json,pathlib,tarfile,subprocess,shutil
P=pathlib.Path('/kaggle/working/hp_round7');out={'os_release':pathlib.Path('/etc/os-release').read_text(),'tools':{n:shutil.which(n) for n in ['clang++-17','ld.lld-17','g++','make','gpg','apt-get']},'space':shutil.disk_usage('/kaggle/working').free}
with tarfile.open(P/'preserved/research_sources_and_candidates.tar.gz','r:gz') as t:
 prefix='src/cmix-lex-transformer/'
 members=[m for m in t.getmembers() if m.name.startswith(prefix)]
 out['source_files']=len(members);out['source_total_bytes']=sum(m.size for m in members if m.isfile())
 out['makefile']=t.extractfile(prefix+'makefile').read().decode()
 out['binaries_objects']=[{'name':m.name,'bytes':m.size} for m in members if m.name.endswith(('.o','.a','.so')) or m.name==prefix+'cmix'][:25]
out['apt_source_files']=[str(p) for p in pathlib.Path('/etc/apt/sources.list.d').glob('*llvm*')]
out['known_trace_files']=[{'name':str(p),'bytes':p.stat().st_size} for p in [P/'lex_finalbit_trace_v1/cmix_trace',P/'cmix_round7_lex_codebook',P/'research_round7_lex_exact_labpatch.py'] if p.exists()]
print(json.dumps(out))
