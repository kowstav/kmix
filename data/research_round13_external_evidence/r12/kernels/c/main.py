"""R12 private CPU commit: long warm native stream + online replay of every arm.

Pre-registered before any output is seen:
  * cluster A: canonical offset 0; cluster B: canonical offset 300,000,000.
  * one unchanged native encoder (lexth11c C3 model, observer build sha 17768b06...),
    window 512 KiB, all windows recorded with their history length.
  * arms: identity; frozen wider law (a=1); round-9 adaptive law; integer mixer
    full {250,1000,4000}, full_1000 with decoded-class contexts, no_explicit_nn,
    global, memory_zero, long_memory.
  * analysis: per-window gain versus history length; cluster B windows with
    history < 8 MiB are warm-up.  Replay only: no candidate archive is produced.
"""
CLUSTER = 'C'
import hashlib, json, os, shutil, sys, time, traceback
from pathlib import Path
T0 = time.monotonic()
OUT = Path('/kaggle/working/r12'); OUT.mkdir(parents=True, exist_ok=True)
M = {'id': f'R12-warm-stream-{CLUSTER}', 'status': 'PREPARING', 'started_unix': time.time(), 'paid_usd': 0,
     'GPU': False, 'deletions': [], 'replay_only': True}
def save():
    (OUT / 'manifest.json').write_text(json.dumps(M, indent=1))
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while b := f.read(1 << 22): h.update(b)
    return h.hexdigest()
try:
    found = list(Path('/kaggle/input').rglob('r12_manifest.json'))
    assert len(found) == 1, [str(f) for f in found]
    A = found[0].parent; meta = json.loads(found[0].read_text())
    for name, info in meta['files'].items():
        p = A / name
        assert p.stat().st_size == info['bytes'], name
        assert sha(p) == info['sha256'], name
    M['asset_manifest_sha256'] = sha(found[0]); M['assets_verified'] = True
    M['affinity'] = sorted(os.sched_getaffinity(0)); M['cpu_count'] = os.cpu_count()
    M['topology'] = [open(f'/sys/devices/system/cpu/cpu{i}/topology/thread_siblings_list').read().strip() for i in range(os.cpu_count())]
    R = Path('/root/r12nb'); (R / 'code').mkdir(parents=True)
    for f in ['stream_replay.cpp', 'integer_mixer.h', 'long_memory.h', 'probability_tables.inc', 'r12_driver.py']:
        shutil.copy2(A / f, R / 'code' / f)
    shutil.copy2(A / 'native_cmix', R / 'cmix'); os.chmod(R / 'cmix', 0o755)
    sys.path.insert(0, str(R / 'code')); import r12_driver as d
    M['consumer_build'] = d.compile_consumer(R / 'code', R / 'stream_replay'); save()
    sl = meta['slices'][CLUSTER]
    data = (A / sl['file']).read_bytes(); assert len(data) == sl['bytes']
    topo = M['topology']
    cpu_enc, cpu_cons = 0, next(i for i in range(os.cpu_count()) if str(0) not in topo[i].split(',') and i != 0)
    budget = 10.6 * 3600 - (time.monotonic() - T0)
    M['status'] = 'RUNNING'; M['budget_seconds'] = budget; save()
    rec = d.run_case(label=f'R12_warm_{CLUSTER}', slice_bytes=data, abs_offset=sl['abs_offset'], binary=R / 'cmix',
                     weights=A / 'lex_h1_run11.tfwc2', dictionary=A / 'english.dic', vocab=A / 'vocab.bm',
                     consumer=R / 'stream_replay', work=R / 'work', out_dir=OUT, budget_seconds=budget,
                     cpu_encoder=cpu_enc, cpu_consumer=cpu_cons, manifest=M, save=save)
    M['status'] = rec['status']
except BaseException as e:
    M.update(status='FAIL', error=repr(e), traceback=traceback.format_exc())
M['finished_unix'] = time.time(); M['wall_seconds'] = time.monotonic() - T0; save()
print(json.dumps({k: M.get(k) for k in ('status', 'wall_seconds')}))
