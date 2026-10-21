
# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

import pathlib,subprocess,os,json
out=pathlib.Path('/kaggle/working/hp_round7')
for name in ['a','b','c','d']:
    raw=f'/root/hp/slices/{name}2m.bin'
    cost=f'/root/hp/runs/lex_{name}/cost.f32' if name in ['a','b'] else str(out/f'baseline_{name}/cost.f32')
    # Corrected EOF handling, frozen family, no target-tuned new choices.
    for mode in ['balanced','edit']:
        subprocess.run(['python',str(out/str(project_path('research_round7_edit_screen.py'))),'--slice',raw,'--cost',cost,'--dictionary','/root/hp/gen/.dict','--mode',mode,'--json',str(out/f'{name}_corrected_{mode}_screen.json')],check=True)
    if name in ['c','d']:
        for masked,exact in [(False,True),(False,False),(True,False)]:
            tag='exact' if exact else 'masked_edit' if masked else 'edit'
            cmd=['python',str(out/'research_round7_line_edit_screen.py'),'--slice',raw,'--cost',cost,'--dictionary','/root/hp/gen/.dict','--out',str(out/f'{name}_line_{tag}.json')]
            if masked:cmd.append('--mask-digits')
            if exact:cmd.append('--exact')
            subprocess.run(cmd,check=True)
print('CORRECTED_CONFIRMATION_SCREENS_COMPLETE',flush=True)
