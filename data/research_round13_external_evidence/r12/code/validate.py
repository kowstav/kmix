import json, os, sys, time, traceback
from pathlib import Path
sys.path.insert(0, '/root/r12/code')
import r12_driver as d
W = Path('/kaggle/working')
OUT = W / 'hp_round12_claude/validation'; OUT.mkdir(parents=True, exist_ok=True)
M = {'id': 'R12-validation', 'status': 'RUNNING', 'started': time.time(), 'deletions': [], 'paid_usd': 0}
def save(): (OUT / 'manifest.json').write_text(json.dumps(M, indent=1))
try:
    code = Path('/root/r12/code'); exe = Path('/root/r12/stream_replay')
    M['consumer_build'] = d.compile_consumer(code, exe); save()
    stream = W / 'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt'
    common = dict(binary=W/'hp_round8/native_stage_trace_v1/tree/cmix', weights=W/'hp_round7/lex_audit/lex_h1_run11.tfwc2',
                  dictionary=W/'hp_round8/native_stage_trace_v1/tree/dictionary/english.dic', vocab=W/'hp_round7/preserved/data/vocab.bm',
                  consumer=exe, out_dir=OUT, manifest=M, save=save, budget_seconds=6*3600)
    import threading
    def case(label, off, n, ce, cc):
        with open(stream, 'rb') as f: f.seek(off); data = f.read(n)
        d.run_case(label=label, slice_bytes=data, abs_offset=off, work=Path('/root/r12/work_' + label), cpu_encoder=ce, cpu_consumer=cc, **common)
    th = [threading.Thread(target=case, args=('V1_warm_0_2MiB', 0, 2097152, 0, 1)),
          threading.Thread(target=case, args=('V2_cold_G_65000000', 65000000, 524288, 2, 3))]
    for t in th: t.start()
    for t in th: t.join()
    M['status'] = 'COMPLETE' if all(c['status'].startswith('COMPLETE') for c in M['cases']) else 'CHECK'
except BaseException as e:
    M.update(status='FAIL', error=repr(e), traceback=traceback.format_exc())
M['finished'] = time.time(); save()
