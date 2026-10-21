"""P5 development-screen analysis and the pre-registered selection (research_round14_template_freeze_v1.md).

Usage: python research_round14_analyze_template_development_v1.py <evidence_dir>
Totals of actual archive bytes over the 16 development regions per arm; four-cell interaction
per (kind, cap, E) with N = none-left, G = template-left, M = none-right, GM = template-right;
selection = min total among template arms with ctx right (ties: smaller cap, smaller E, static);
advances only if it beats none-right. gzip and zstd totals are reported for the full-code context.
"""
import json, sys, time
from pathlib import Path

R = Path(__file__).resolve().parent
ev = Path(sys.argv[1])
ps = list(ev.rglob('manifest.json')); assert len(ps) == 1
m = json.loads(ps[0].read_text())
assert m['status'] == 'COMPLETE_ALL_PAID_TEMPLATE_INVERSES' and m['role'] == 'development'
cases = m['cases']; regions = sorted({c['index'] for c in cases}); assert regions == list(range(0, 32, 2))
arms = sorted({(c['ctx'], c['kind'], c['cap'], c['edit_cap']) for c in cases}); assert len(arms) == 39
assert len(cases) == 39 * 16 and all(c['exact_inverse'] for c in cases)
tot = {a: sum(c['archive_bytes'] for c in cases if (c['ctx'], c['kind'], c['cap'], c['edit_cap']) == a) for a in arms}
usage = {a: sum(c['stats']['template_runs'] for c in cases if (c['ctx'], c['kind'], c['cap'], c['edit_cap']) == a) for a in arms}
runs = {a: sum(c['stats']['runs'] for c in cases if (c['ctx'], c['kind'], c['cap'], c['edit_cap']) == a) for a in arms}
table = {a: sum(c['channels']['template_table'] for c in cases if (c['ctx'], c['kind'], c['cap'], c['edit_cap']) == a) for a in arms}
stream = {a: sum(c['channels']['run_stream'] for c in cases if (c['ctx'], c['kind'], c['cap'], c['edit_cap']) == a) for a in arms}
for c in cases:
    if c['kind'] == 'none':
        assert c['constructor_codec_identity']['sequence_stream_identical'] is True
gzip_t = sum(c['gzip_bytes'] for c in cases if c['kind'] == 'none' and c['ctx'] == 'right')
zstd_t = sum(c['zstd_bytes'] for c in cases if c['kind'] == 'none' and c['ctx'] == 'right')
base = {ctx: tot[(ctx, 'none', 0, 0)] for ctx in ('left', 'right', 'wrong')}
rows = []
for a in arms:
    ctx, kind, cap, E = a
    rows.append({'ctx': ctx, 'kind': kind, 'cap': cap, 'edit_cap': E, 'total_bytes': tot[a], 'saving_vs_none_same_ctx': base[ctx] - tot[a],
                 'run_stream_bytes': stream[a], 'table_bytes': table[a], 'template_runs': usage[a], 'runs': runs[a]})
inter = []
for kind in ('static', 'prefix'):
    for cap in (64, 256):
        for E in (0, 1, 2):
            N, G = tot[('left', 'none', 0, 0)], tot[('left', kind, cap, E)]
            Mr, GM = tot[('right', 'none', 0, 0)], tot[('right', kind, cap, E)]
            inter.append({'kind': kind, 'cap': cap, 'edit_cap': E, 'interaction_bytes': G + Mr - N - GM,
                          'template_gain_left': N - G, 'template_gain_right': Mr - GM, 'right_gain_direct': N - Mr,
                          'wrong_control_template_gain': tot[('wrong', 'none', 0, 0)] - tot[('wrong', kind, cap, E)]})
cands = [a for a in arms if a[0] == 'right' and a[1] != 'none']
sel = min(cands, key=lambda a: (tot[a], a[2], a[3], 0 if a[1] == 'static' else 1))
advances = tot[sel] < base['right']
out = {'time': time.time(), 'manifest': str(ps[0]), 'regions': regions, 'arms': rows, 'four_cell_interaction': inter,
       'baselines': base, 'gzip_total': gzip_t, 'zstd_total': zstd_t,
       'selected': {'ctx': sel[0], 'kind': sel[1], 'cap': sel[2], 'edit_cap': sel[3], 'total_bytes': tot[sel],
                    'saving_vs_none_right': base['right'] - tot[sel]},
       'advances_to_confirmation': advances, 'worker_CPU_seconds': m.get('worker_CPU_seconds'), 'effective_cores': m.get('effective_cores'),
       'note': 'actual paid archive bytes; tables paid per archive; raw-text proxy, not the native stream'}
(R / 'research_round14_template_development_analysis_v1.json').write_text(json.dumps(out, indent=2))
print(json.dumps({k: out[k] for k in ('baselines', 'gzip_total', 'zstd_total', 'selected', 'advances_to_confirmation')}, indent=1))
for r in sorted(rows, key=lambda r: r['total_bytes'])[:12]: print(r)
for i in inter: print(i)
