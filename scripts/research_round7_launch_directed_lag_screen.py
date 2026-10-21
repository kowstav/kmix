"""Exclusive detached Kaggle launch; inspect existing jobs/results first."""
import json
import pathlib
import subprocess

out = pathlib.Path('/kaggle/working/hp_round7')
script = out / 'research_round7_directed_lag_screen.py'
assert script.is_file() and not (out / 'idea_arch_directed_lag_v1').exists(), 'Preserve existing results; do not duplicate'
args = subprocess.check_output(['ps', '-eo', 'args'], text=True).splitlines()
assert not any(str(script) in s for s in args), 'Directed lag job already active'
with (out / 'idea_arch_directed_lag_v1_controller.log').open('x') as log:
    p = subprocess.Popen(['python3', '-u', str(script)], cwd=out, stdout=log,
                         stderr=subprocess.STDOUT, start_new_session=True)
print(json.dumps({'started_pid': p.pid, 'job': 'I04_directed_lag_v1',
                  'neural_training': False, 'paid_rental_usd': 0, 'deletions': []}))
