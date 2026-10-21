import pathlib,json,subprocess
hp=pathlib.Path('/root/hp');out=pathlib.Path('/kaggle/working/hp_round7')
print('CANDMAKE',(hp/'cand_final2/makefile').read_text()[:1500])
print('CANDRUN',[(p.name,p.stat().st_size) for p in (hp/'cand_final2/run').iterdir() if p.is_file() and not p.is_symlink()])
print('CANDSRC',[(p.name,p.is_dir()) for p in (hp/'cand_final2/src').iterdir()])
for p in [hp/'round7_lab/cpp_infer/src/opt/glue.cpp',hp/'round7_lab/cpp_infer/src/opt/arena_build.cpp']:
    lines=p.read_text().splitlines();print(p.name,'\n'.join(x for x in lines if 'FX2TFW' in x or 'compressed' in x or 'DT_F32' in x or 'DT_BF16' in x))
print('CODEC',(out/'v5_codec.log').read_text()[-1800:])
print('SX',(out/'sx_topology_controls.json').read_text())
print('AVAILABLE_TOOLS',subprocess.check_output(['which','upx','clang++-17'],text=True))
