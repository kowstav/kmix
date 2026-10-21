import json,pathlib
s=json.loads(pathlib.Path('research_round7_session355529591_preprocess_sources.json').read_text())['src/fx2-cmix-transformer-v1/src/runner.cpp']
for pattern in ["mode == 'x'","mode == 's'",'split4Decomp();','SavePpmdBytes(temp_path']:
 at=s.find(pattern);print(pattern,at);print(s[max(0,at-180):at+1500] if at>=0 else '')
