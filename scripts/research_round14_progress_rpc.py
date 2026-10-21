from pathlib import Path
import json,subprocess,shutil
W=Path('/kaggle/working/hp_round14');p=W/'pull_manifest.json';m=json.loads(p.read_text())
out={'status':m['status'],'error':m.get('error'),'finished':m.get('finished'),'compact':m.get('compact'),
     'pulls':[{'ref':r['ref'],'exit':r['exit'],'files':len(r['files'])} for r in m['pulls']],
     'disk_free':shutil.disk_usage('/kaggle/working').free}
print(json.dumps(out))
