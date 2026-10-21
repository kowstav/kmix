"""R12 interactive fallback: two 24 MiB warm streams (C at 450,000,000 and A at 0) with consumer v2
(all v1 arms + reduced_250, minimal_250, guarded_fixedshare).  Registered after notebook C v2 died
without output; parameters fixed before any warm-C result exists."""
import json, subprocess, sys, threading, time, traceback
from pathlib import Path
sys.path.insert(0, '/root/r12/code'); import r12_driver as d
W = Path('/kaggle/working'); OUT = W / 'hp_round12_claude/warm_fallback'; OUT.mkdir(parents=True, exist_ok=True)
M = {'id': 'R12-warm-fallback', 'status': 'RUNNING', 'started': time.time(), 'deletions': [], 'paid_usd': 0}
lock = threading.Lock()
def save():
    with lock: (OUT / 'manifest.json').write_text(json.dumps(M, indent=1))
try:
    exe = Path('/root/r12/stream_replay_v2')
    r = subprocess.run(['g++', '-O2', '-std=c++17', '-fno-fast-math', '-ffp-contract=off', '-I', '/root/r12/code',
                        str(W / 'hp_round12_claude/code/stream_replay_v2.cpp'), '-o', str(exe)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-1500:]
    M['consumer_v2_sha256'] = d.sha(exe); save()
    stream = W / 'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt'
    common = dict(binary=W / 'hp_round8/native_stage_trace_v1/tree/cmix', weights=W / 'hp_round7/lex_audit/lex_h1_run11.tfwc2',
                  dictionary=W / 'hp_round8/native_stage_trace_v1/tree/dictionary/english.dic', vocab=W / 'hp_round7/preserved/data/vocab.bm',
                  consumer=exe, out_dir=OUT, manifest=M, save=save, budget_seconds=7 * 3600, keep_cost=True)
    def case(label, off, ce, cc):
        with open(stream, 'rb') as f: f.seek(off); data = f.read(24 * 1048576)
        d.run_case(label=label, slice_bytes=data, abs_offset=off, work=Path('/root/r12/' + label), cpu_encoder=ce, cpu_consumer=cc, **common)
    th = [threading.Thread(target=case, args=('fallback_C_450000000', 450000000, 0, 2)),
          threading.Thread(target=case, args=('fallback_A_0', 0, 1, 3))]
    for t in th: t.start()
    for t in th: t.join()
    M['status'] = 'COMPLETE'
except BaseException as e:
    M.update(status='FAIL', error=repr(e), traceback=traceback.format_exc())
M['finished'] = time.time(); save()
