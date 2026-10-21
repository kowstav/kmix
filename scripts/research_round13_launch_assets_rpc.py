from pathlib import Path
import json,os,subprocess
p=Path('/kaggle/working/hp_round13/asset_prepare_manifest.json')
if p.exists():print(json.dumps({'action':'REUSE','manifest':json.loads(p.read_text())}))
else:
    log=Path('/kaggle/working/hp_round13/asset_prepare_controller.log');log.parent.mkdir(exist_ok=True)
    with log.open('x') as f:
        process=subprocess.Popen(['python3','/kaggle/working/hp_round13/prepare_assets_worker.py'],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'action':'LAUNCHED','pid':process.pid,'manifest':str(p)}))
