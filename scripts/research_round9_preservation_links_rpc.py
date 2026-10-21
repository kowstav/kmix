import pathlib,json,os,hashlib
R=pathlib.Path('/kaggle/working/hp_round9');L=R/'preservation_links';L.mkdir(exist_ok=True);out=[]
for name in ['core_extension_v1','word_features_v1','word_softmax_v1','word_softmax_v2','word_warmstart_v1','core_distributed_v1','core_distributed_v2']:
 p=R/name/'manifest.json'
 if not p.exists():continue
 j=json.loads(p.read_text());target=L/name;target.mkdir(exist_ok=True)
 for row in j.get('rungs',[])+j.get('word_rungs',[]):
  f=pathlib.Path(row['checkpoint_path']);dest=target/f.name
  assert f.is_file() and f.resolve().is_relative_to(pathlib.Path('/root/hp_round9').resolve())
  if dest.is_symlink():assert dest.resolve()==f.resolve()
  else:assert not dest.exists();dest.symlink_to(f)
  out.append({'job':name,'remote_path':str(dest.relative_to('/kaggle/working')),'filename':f.name,'bytes':f.stat().st_size,'sha256':row['checkpoint_sha256']})
(R/'preservation_links_manifest.json').write_text(json.dumps({'status':'ROOT_CHECKPOINT_LINKS_READY','files':out,'deletions':[]},indent=2));print(json.dumps({'count':len(out),'bytes':sum(x['bytes'] for x in out),'symlinks_add_no_duplicate_checkpoint_bytes':True}))
