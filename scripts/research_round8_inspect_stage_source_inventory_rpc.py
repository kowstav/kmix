import json,pathlib
T=pathlib.Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree');files=[]
for d in ['src','dictionary']:files.extend(p for p in (T/d).rglob('*') if p.is_file() and p.suffix!='.o')
print(json.dumps({'files':len(files),'bytes':sum(p.stat().st_size for p in files),'largest':[{'file':p.relative_to(T).as_posix(),'bytes':p.stat().st_size} for p in sorted(files,key=lambda p:p.stat().st_size,reverse=True)[:8]],'root_files':[p.name for p in T.iterdir() if p.is_file()]}))
