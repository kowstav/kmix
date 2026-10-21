from pathlib import Path
import subprocess,json
W=Path('/kaggle/working/hp_round14');assert not (W/'tail_collection_v1.json').exists()
p=subprocess.Popen(['python3','/kaggle/working/research_round14_pull_tail_worker.py'],stdout=(W/'tail_pull.log').open('ab'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'action':'collect_native_completion_and_article_order_failure'}))
