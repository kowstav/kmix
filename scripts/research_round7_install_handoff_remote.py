import hashlib,json,pathlib
r=pathlib.Path('/kaggle/working/hp_round7');j=json.loads((r/'research_round7_handoff_20261005.json').read_text());d=r/'handoff_20261005';assert not d.exists();d.mkdir()
for x in j['files']:
 assert pathlib.Path(x['path']).name==x['path'];b=x['text'].encode('utf8');assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'];(d/x['path']).write_bytes(b)
(d/'index.json').write_text(json.dumps([{k:v for k,v in x.items() if k!='text'} for x in j['files']],indent=2));print(json.dumps({'saved':str(d),'files':len(j['files']),'no_jobs_launched':True,'deletions':[]}))
