def _hp_round7_inspect_recovery():
    import pathlib,json,subprocess,os
    hp=pathlib.Path('/root/hp'); result={}
    for name in ['cand_final2/src/runner.cpp','cand_final2/src/predictor.cpp','src/fx2-cmix-transformer-v1/makefile','tools/build_candidate2.sh','src/cmix-lex-transformer/README.md']:
        p=hp/name
        if p.exists():
            if name.endswith('runner.cpp'): result[name]={'LAB_RAW_count':p.read_text().count('LAB_RAW'),'LAB_COST_count':p.read_text().count('LAB_COST')}
            elif name.endswith('predictor.cpp'): result[name]={'LAB_SX_count':p.read_text().count('LAB_SX'),'LAB_KEEP_PPMD_count':p.read_text().count('LAB_KEEP_PPMD')}
            else: result[name]=p.read_text()[:10000]
    for command in [['/root/hp/cand_final2/run/cmix_orig','--help'],['g++','--version']]:
        r=subprocess.run(command,capture_output=True,text=True,timeout=15)
        result[' '.join(command)]={'rc':r.returncode,'out':r.stdout[:10000],'err':r.stderr[:1000]}
    print(json.dumps(result))
_hp_round7_inspect_recovery()
del _hp_round7_inspect_recovery
