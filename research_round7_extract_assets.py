import json, sys
from pathlib import Path
root=Path(__file__).resolve().parent
message=json.loads((root/(sys.argv[1] if len(sys.argv)>1 else 'research_round7_assets.json')).read_text())
data=json.loads(''.join(s['text'] for s in message['streams'] if s['name']=='stdout'))
out=root/'research_round7_sources'; out.mkdir(exist_ok=True)
for name, content in data['files'].items():
    (out/Path(name).name).write_text(content,encoding='utf-8')
(out/'asset_lists.json').write_text(json.dumps(data.get('lists',{}),indent=2))
print('Extracted',len(data['files']),'source files')
