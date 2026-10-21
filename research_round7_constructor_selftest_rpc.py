import pathlib,subprocess
root=pathlib.Path('/kaggle/working/hp_round7')
subprocess.run(['python3','-u',str(root/'research_round7_constructor_split.py'),'--selftest'],cwd=root,check=True)
