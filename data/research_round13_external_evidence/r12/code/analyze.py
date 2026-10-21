"""R12 analysis: warm clusters vs cold controls.  Gains are byte equivalents (bits/8),
positive = candidate smaller.  Blocks of 8 consecutive 512 KiB windows (4 MiB) are
treated as dependence clusters within a stream; streams A/B/C are independent regions."""
import json, math, os, subprocess, glob
from pathlib import Path
import numpy as np
W = Path('/kaggle/working/hp_round12_claude'); P = Path('/root/r12_pull')
from kaggle_secrets import UserSecretsClient
env = dict(os.environ); env['KAGGLE_API_TOKEN'] = UserSecretsClient().get_secret('kaggle_api_token')
out = {'streams': {}, 'cold': {}, 'paired': []}
for c in 'abc':
    dest = P / f'warm_{c}'; dest.mkdir(parents=True, exist_ok=True)
    if not list(dest.rglob('*.jsonl')):
        r = subprocess.run(['kaggle', 'kernels', 'output', f'chaoscpp/hutter-r12-warm-stream-{c}', '-p', str(dest)], capture_output=True, text=True, env=env, timeout=1800)
        out.setdefault('pull', {})[c] = r.returncode
    files = list(dest.rglob('R12_warm_*.jsonl'))
    man = list(dest.rglob('manifest.json'))
    if not files:
        out['streams'][c.upper()] = {'status': 'NO_OUTPUT', 'manifest': json.loads(man[0].read_text()).get('status') if man else None}
        continue
    m = json.loads(man[0].read_text()) if man else {}
    rows = [json.loads(l) for l in files[0].read_text().splitlines() if l.strip()]
    win = [r for r in rows if r.get('type') == 'window' and not r['partial']]
    summ = next((r for r in rows if r.get('type') == 'summary'), None)
    arms = list(win[0]['arms'].keys())
    G = {a: np.array([(r['baseline_bits'] - r['arms'][a]) / 8 for r in win]) for a in arms}
    hist = np.array([r['history_bytes'] for r in win]); base = np.array([r['baseline_bits'] / 8 for r in win])
    case = (m.get('cases') or [{}])[0]
    st = {'status': m.get('status'), 'windows': len(win), 'bytes': summ['bytes'] if summ else None,
          'abs_offset': win[0]['abs_offset'], 'identity_mismatch': summ['identity_mismatch_bits'] if summ else None,
          'punch_failed': summ['punch_failed'] if summ else None, 'encode': case.get('encode'), 'stopped_early': case.get('stopped_early'),
          'baseline_minus_cost_bits': case.get('baseline_minus_cost_bits'), 'archive_bytes': case.get('archive_bytes'),
          'baseline_bits_per_byte_by_bucket': {}, 'gain_by_bucket': {}, 'warm_ge_8MiB': {}}
    buckets = [(0, 524288), (524288, 2 << 20), (2 << 20, 8 << 20), (8 << 20, 32 << 20), (32 << 20, 64 << 20)]
    for lo, hi in buckets:
        sel = (hist >= lo) & (hist < hi)
        if not sel.any(): continue
        key = f'{lo >> 10}K-{hi >> 10}K'
        st['baseline_bits_per_byte_by_bucket'][key] = float(base[sel].sum() * 8 / (sel.sum() * 524288))
        st['gain_by_bucket'][key] = {a: round(float(G[a][sel].mean()), 2) for a in arms}
    sel = hist >= (8 << 20)
    nb = int(sel.sum()) // 8
    for a in arms:
        g = G[a][sel][:nb * 8].reshape(nb, 8).sum(1) if nb else np.array([])  # bytes per 4 MiB block
        if nb >= 2:
            mean = g.mean(); se = g.std(ddof=1) / math.sqrt(nb)
            tcrit = {2: 12.71, 3: 4.30, 4: 3.18, 5: 2.78, 6: 2.57, 7: 2.45, 8: 2.36, 9: 2.31, 10: 2.26, 11: 2.23, 12: 2.20, 13: 2.18, 14: 2.16}.get(nb, 2.1)
            st['warm_ge_8MiB'][a] = {'blocks': nb, 'mean_bytes_per_4MiB': round(float(mean), 2), 'ci95': [round(float(mean - tcrit * se), 2), round(float(mean + tcrit * se), 2)],
                                     'rate_bytes_per_input_byte': float(mean / 4194304), 'full_file_projection_bytes_if_stationary': float(mean / 4194304 * 587138826)}
    st['per_window'] = [{'h': int(h), 'base': round(float(b), 1), **{a: round(float(G[a][i]), 2) for a in arms if a != 'mixer_identity'}} for i, (h, b) in enumerate(zip(hist, base))]
    out['streams'][c.upper()] = st
# cold controls
cm = json.loads((W / 'cold/manifest.json').read_text())
for case in cm.get('cases', []):
    s = case.get('summary')
    if not s: continue
    b = s['baseline_bits']
    out['cold'][case['abs_offset']] = {'baseline_B': b / 8, **{a: (b - v) / 8 for a, v in s['totals'].items()}}
# paired comparison on matched windows
for st_name, st in out['streams'].items():
    if 'per_window' not in st: continue
    for w in st['per_window']:
        absoff = st['abs_offset'] + w['h']
        if absoff in out['cold']:
            cold = out['cold'][absoff]
            out['paired'].append({'stream': st_name, 'abs_offset': absoff, 'history_bytes': w['h'],
                                  'baseline_cold_B': round(cold['baseline_B'], 1), 'baseline_warm_B': w['base'],
                                  'cold_penalty_pct': round(100 * (cold['baseline_B'] / w['base'] - 1), 2),
                                  **{f'{a}_cold': round(cold[a], 1) for a in ('adaptive_law_r9', 'wider_frozen_a1', 'mixer_full_250', 'mixer_global_1000', 'mixer_memory_zero_1000')},
                                  **{f'{a}_warm': w.get(a) for a in ('adaptive_law_r9', 'wider_frozen_a1', 'mixer_full_250', 'mixer_global_1000', 'mixer_memory_zero_1000')}})
(W / 'analysis.json').write_text(json.dumps(out, indent=1))
lite = {k: v for k, v in out.items() if k != 'streams'}
lite['streams'] = {k: {kk: vv for kk, vv in v.items() if kk != 'per_window'} for k, v in out['streams'].items()}
print(json.dumps(lite, indent=1)[:20000])
