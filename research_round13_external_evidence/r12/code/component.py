"""R12 clean component timing (repairs the round-10 component job, which demanded
-d decodes for --ppmd-only/--transformer-only; cmix rejects those flags in -d).
Encode-only timing, one process at a time, pinned to cpu0 with its SMT sibling idle.
Marginal per-byte cost = (T(3 MiB) - T(1 MiB)) / 2 MiB removes startup cost."""
import json, os, subprocess, time
from pathlib import Path
W = Path('/kaggle/working'); OUT = W / 'hp_round12_claude/component'; OUT.mkdir(parents=True, exist_ok=True)
B = W / 'hp_round8/native_stage_trace_v1/tree/cmix'; WT = W / 'hp_round7/lex_audit/lex_h1_run11.tfwc2'
DICT = W / 'hp_round8/native_stage_trace_v1/tree/dictionary/english.dic'; VOCAB = W / 'hp_round7/preserved/data/vocab.bm'
STREAM = W / 'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt'
M = {'id': 'R12-component-timing', 'status': 'WAITING_FOR_COLD', 'runs': [], 'deletions': [], 'paid_usd': 0}
def save(): (OUT / 'manifest.json').write_text(json.dumps(M, indent=1))
save()
while True:   # never contend with the cold-control encoders
    try:
        if json.loads((W / 'hp_round12_claude/cold/manifest.json').read_text()).get('status') != 'RUNNING': break
    except Exception: pass
    time.sleep(60)
M['status'] = 'RUNNING'; save()
modes = {'combined': ['--transformer', str(WT)], 'transformer_only': ['--transformer', str(WT), '--transformer-only'], 'ppmd_only': ['--ppmd-only']}
env = {k: v for k, v in os.environ.items() if not k.startswith(('LAB_', 'FX_PREPARE', 'HP_LEX_'))}
env.update(LAB_RAW='1', LAB_VOCAB=str(VOCAB), LAB_DICT=str(DICT), OMP_NUM_THREADS='1')
for size in (1048576, 3145728):
    for mode, flags in modes.items():
        work = Path(f'/root/r12/comp_{mode}_{size}'); work.mkdir(parents=True, exist_ok=False)
        with open(STREAM, 'rb') as f: (work / 'input.bin').write_bytes(f.read(size))
        (work / '.dict').symlink_to(DICT)
        t = time.monotonic()
        p = subprocess.Popen([str(B), '-n', *flags, 'input.bin', 'out.cmx'], cwd=work, env=env, stdout=subprocess.DEVNULL,
                             stderr=open(work / 'stderr.log', 'wb'), preexec_fn=lambda: os.sched_setaffinity(0, {0}))
        _, status, ru = os.wait4(p.pid, 0)
        M['runs'].append({'mode': mode, 'bytes': size, 'exit': os.waitstatus_to_exitcode(status), 'wall_s': time.monotonic() - t,
                          'user_s': ru.ru_utime, 'sys_s': ru.ru_stime, 'peak_RSS_KiB': ru.ru_maxrss,
                          'archive_bytes': (work / 'out.cmx').stat().st_size if (work / 'out.cmx').exists() else None})
        save()
by = {(r['mode'], r['bytes']): r for r in M['runs']}
M['marginal_us_per_byte'] = {m: 1e6 * ((by[(m, 3145728)]['user_s'] + by[(m, 3145728)]['sys_s']) - (by[(m, 1048576)]['user_s'] + by[(m, 1048576)]['sys_s'])) / 2097152 for m in modes}
mc = M['marginal_us_per_byte']
M['marginal_share'] = {'ppmd_of_combined': mc['ppmd_only'] / mc['combined'],
                       'transformer_only_of_combined': mc['transformer_only'] / mc['combined'],
                       'classical_bank_and_mixing_of_combined': (mc['combined'] - mc['transformer_only']) / mc['combined']}
M['status'] = 'COMPLETE'; save()
