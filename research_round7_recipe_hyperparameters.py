import json,pathlib
j=json.loads(pathlib.Path('research_round7_training_readiness_source_audit.json').read_text())
for x in j['source_snippets']:
 if x['path'].endswith(('train_6m.py','quantize.py','cooldown.py')):
  a=x['text'].splitlines();out=[line.strip() for line in a if any(k in line for k in ['learning_rate:', 'weight_decay=', 'momentum=', 'betas=', 'adjust_lr_fn=', 'warmup_epochs:', 'epochs:'])]
  print(json.dumps({'source':x['path'],'sha256':x['sha256'],'hyperparameters':out}))
