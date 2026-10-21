def _hp_build_parameters():
    import pathlib,json
    hp=pathlib.Path('/root/hp')
    found={}
    for root in [hp/'tools',hp/'src/fx2-cmix-transformer-v1',hp/'cand_final2']:
        for p in root.rglob('*'):
            if p.is_file() and not p.is_symlink() and p.stat().st_size<100000 and p.suffix not in ['.o','.tch','.fx2tfwc2']:
                try: lines=p.read_text().splitlines()
                except (UnicodeDecodeError,OSError): continue
                hits=[l for l in lines if 'CFLAGS_DEFINES' in l or ('UPDATE_LIMIT' in l and '-D' in l)]
                if hits: found[str(p)]=hits
    print(json.dumps(found))
_hp_build_parameters()
del _hp_build_parameters
