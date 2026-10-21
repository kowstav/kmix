import pathlib,json,shutil
R=pathlib.Path('/kaggle/working/hp_round9');p=R/'compact_preservation_v1/manifest.json';j=json.loads(p.read_text()) if p.exists() else {};print(json.dumps({k:j.get(k) for k in ['status','pid','stage','archive_bytes','archive_sha256','error']}));print(json.dumps({'working_free':shutil.disk_usage('/kaggle/working').free,'root_free':shutil.disk_usage('/root').free}))
