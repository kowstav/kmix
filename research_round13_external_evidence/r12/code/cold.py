"""R12 cold controls: the same 512 KiB windows as the warm streams, coded from a
cold start (fresh native process, fresh arms).  Registered before warm results.
H (375,000,000) reproduces the published adaptive-law archive (+172 B)."""
import json, queue, sys, threading, time, traceback
from pathlib import Path
sys.path.insert(0, '/root/r12/code')
import r12_driver as d
W = Path('/kaggle/working'); OUT = W / 'hp_round12_claude/cold'; OUT.mkdir(parents=True, exist_ok=True)
MiB = 1048576; K = 524288
windows = ([('A', o * MiB) for o in (4, 12, 24, 36, 48, 60)] + [('B', 300000000 + o * MiB) for o in (12, 24, 36, 48, 60)]
           + [('H', 375000000)])
M = {'id': 'R12-cold-controls', 'status': 'RUNNING', 'started': time.time(), 'windows': windows, 'deletions': [], 'paid_usd': 0}
lock = threading.Lock()
def save():
    with lock: (OUT / 'manifest.json').write_text(json.dumps(M, indent=1))
stream = W / 'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt'
common = dict(binary=W / 'hp_round8/native_stage_trace_v1/tree/cmix', weights=W / 'hp_round7/lex_audit/lex_h1_run11.tfwc2',
              dictionary=W / 'hp_round8/native_stage_trace_v1/tree/dictionary/english.dic', vocab=W / 'hp_round7/preserved/data/vocab.bm',
              consumer=Path('/root/r12/stream_replay'), out_dir=OUT, manifest=M, save=save, budget_seconds=3 * 3600, keep_cost=False)
q = queue.Queue()
for w in windows: q.put(w)
def worker(cpu_enc, cpu_cons, wait_for_v1):
    if wait_for_v1:
        while True:
            try:
                v = json.loads((W / 'hp_round12_claude/validation/manifest.json').read_text())
                if v.get('status') != 'RUNNING': break
            except Exception: pass
            time.sleep(30)
    while True:
        try: cluster, off = q.get_nowait()
        except queue.Empty: return
        try:
            with open(stream, 'rb') as f: f.seek(off); data = f.read(K)
            d.run_case(label=f'cold_{cluster}_{off}', slice_bytes=data, abs_offset=off, work=Path(f'/root/r12/cold_{off}'),
                       cpu_encoder=cpu_enc, cpu_consumer=cpu_cons, **common)
        except BaseException as e:
            with lock: M.setdefault('errors', []).append({'window': off, 'error': repr(e), 'tb': traceback.format_exc()})
            save()
try:
    th = [threading.Thread(target=worker, args=(3, 2, False)), threading.Thread(target=worker, args=(0, 1, True))]
    for t in th: t.start()
    for t in th: t.join()
    M['status'] = 'COMPLETE' if all(c['status'] == 'COMPLETE' for c in M['cases']) and not M.get('errors') else 'CHECK'
except BaseException as e:
    M.update(status='FAIL', error=repr(e), traceback=traceback.format_exc())
M['finished'] = time.time(); save()
