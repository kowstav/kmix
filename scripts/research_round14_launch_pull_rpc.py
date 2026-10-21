from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');W.mkdir(exist_ok=True)
p=W/'pull_manifest.json'
if p.exists():print(p.read_text())
else:
    child=subprocess.Popen(['python','/root/research_round14_pull_worker.py'],stdin=subprocess.DEVNULL,
        stdout=(W/'pull.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'launched_pid':child.pid,'manifest':str(p)}))
