import json,pathlib
r=json.loads(pathlib.Path('research_round7_session355529591_source_readiness.json').read_text())
for name,text in r['source'].items():
 print('\nFILE',name)
 if name.endswith(('make_training_data.sh','preprocess_roundtrip.cpp','preprocessor.h')):print(text[:15500])
 elif name.endswith('runner.cpp'):
  lines=text.splitlines()
  for i,l in enumerate(lines):
   if any(t in l for t in ('Usage','preprocess_only','Preprocess','argc','strcmp(argv','Generate','case \'p\'')):
    print('\n'.join(lines[max(0,i-3):i+12]))
 elif name.endswith('genprobs.py'):print(text[:3500])
