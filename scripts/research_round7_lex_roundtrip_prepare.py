import pathlib,subprocess,json,shutil,hashlib,time
out=pathlib.Path('/kaggle/working/hp_round7');lab=pathlib.Path('/root/hp/lex_matched_lab');dest=pathlib.Path('/root/hp/lex_roundtrip_lab')
assert 'LEX_BUILD_COMPLETE' in (out/'lex_exact_build.log').read_text()
assert not dest.exists();shutil.copytree(lab,dest)
log=(out/'lex_exact_build.log').read_text();commands=[x for x in log.splitlines() if x.startswith('clang++-17 ')]
print('COMPILED_COMMANDS',len(commands),'NEURAL_COMMANDS',sum('tf_' in x for x in commands),'CLASSICAL_COMMANDS',sum('DPPMD_MEM_MB=3500' in x for x in commands))
p=dest/'src/runner.cpp';s=p.read_text()
old='      preprocessor::Pretrain(&p, dictionary);\n    }\n\n    std::ofstream temp_out'
new='      preprocessor::Pretrain(&p, dictionary);\n    } else if(getenv("LAB_DICT")&&!extraction.ppmd_only&&!extraction.transformer_only){\n      FILE* f=fopen(getenv("LAB_DICT"),"rb");if(!f)Fail("LAB_DICT unreadable");preprocessor::Pretrain(&p,f);fclose(f);\n    }\n\n    std::ofstream temp_out'
assert s.count(old)==1;s=s.replace(old,new)
old='\n  preprocessor::Decode(temp_in, data_out, dictionary);'
new='\n  if(getenv("LAB_RAW")){\n    char buf[1<<20];size_t n;while((n=fread(buf,1,sizeof(buf),temp_in)))fwrite(buf,1,n,data_out);\n  } else preprocessor::Decode(temp_in, data_out, dictionary);'
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
flags='-DSEED=923 -DUPDATE_LIMIT=3000 -DPPMD_MEM_MB=3500 -DCMIX_L0_LR_SCALE=0.6 -DCMIX_L1_LR_SCALE=0.25 -DCMIX_L0_MIXER_MASK=0x42e72du -DFXCM_CM_DIV=2'
tf='-DQMAT_CODEBOOK=1 -DQMAT_WMAX=21 -DQMAT_SMALL_W8=1 -DTF_ACTQ_DYN=1 -DTF_AVX512=1'
# Force the complete compile once: make does not track command-line flag changes.
# No clean/delete; all earlier source/build copies remain available.
with (out/'lex_roundtrip_build.log').open('w') as f:
    subprocess.run(['make','-B','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+flags,'CFLAGS_TF_DEFINES='+tf],cwd=dest,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=1500)
shutil.copy2(dest/'cmix',out/'cmix_round7_lex_roundtrip')
print('LEX_ROUNDTRIP_BUILD_COMPLETE',flush=True)
