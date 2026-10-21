"""Eight-region joint confirmation: guard G vs guard+match-pruning GM on IDs 8..15.

Joint A = 8,10,12,14 (tag joint-a-20261009-2325), joint B = 9,11,13,15 (tag
joint-b-20261010-0446). Guard baseline must equal the historical mode-2 guard
(archive, every Q16, warm bits) on all eight regions. Byte interaction uses the
component confirmation N/M rows of the same inputs (A wave for even IDs, B wave for
odd IDs) after input and binary identity checks. CPU is compared only inside one
notebook. Eight clusters: descriptive only, no interval.
"""
from pathlib import Path
import hashlib, json, statistics, time

R = Path(__file__).resolve().parent
JOINT = {'a': R / 'research_round14_confirmation_compact_joint-a-20261009-2325_evidence',
         'b': R / 'research_round14_confirmation_compact_joint-b-20261010-0446_evidence'}
COMP = {'a': R / 'research_round14_confirmation_compact_a-20261009-1734_evidence',
        'b': R / 'research_round14_confirmation_compact_b-20261009-2328_evidence'}
BIN_N = '30b539b3ec2cd0a2adf51d3103f2643d113022cce2c7fb17b9828b6f61e10fda'
BIN_M = 'cf8fc836f7225f2b25b48d76ffb5ce3bf0682f91549082a1d4ba0353755c8a6e'
BIN_G = '5f6e0c7b8be11894e979033a94206b7523796656be590794d78d81e9739cb657'   # packed16 guard
BIN_GM = '0c29a8c3c90ab04428273f0bfb9f055feb97acf1b520a372ef8362cd076204f5'


def cpu(c, ph): return c[ph]['CPU_user_seconds'] + c[ph]['CPU_system_seconds']


hist = {}
for p in (R / 'research_round14_batch_evidence').glob('hutter-r14-native-confirmation-*/native-confirmation/manifest.json'):
    for r in json.loads(p.read_text())['regions']:
        for c in r['cases']:
            hist[(r['region'], str(c['mode']))] = c
comp = {}
for wave, d in COMP.items():
    for p in d.rglob('manifest.json'):
        m = json.loads(p.read_text())
        for r in m['regions']:
            for c in r['cases']:
                if c['mode'] in ('neutral', 'prune_match'):
                    comp[(r['region'], c['mode'])] = c
rows, notebooks = [], {}
for wave, d in JOINT.items():
    ps = list(d.rglob('manifest.json')); assert len(ps) == 1
    m = json.loads(ps[0].read_text())
    ids = [8, 10, 12, 14] if wave == 'a' else [9, 11, 13, 15]
    assert m['status'] == 'COMPLETE_FOUR_NATIVE_GUARD_MATCH_PAIRS' and m['run_label'] == 'confirmation_' + wave
    assert sorted(r['region'] for r in m['regions']) == ids == m['registered_regions']
    nb_rows = []
    for reg in sorted(m['regions'], key=lambda r: r['region']):
        i = reg['region']; by = {c['mode']: c for c in reg['cases']}; g, gm = by['guard_base'], by['guard_match']
        n, mp = comp[(i, 'neutral')], comp[(i, 'prune_match')]
        assert g['exact_independent_inverse'] is True and gm['exact_independent_inverse'] is True
        assert g['binary_sha256'] == BIN_G and gm['binary_sha256'] == BIN_GM
        assert n['binary_sha256'] == BIN_N and mp['binary_sha256'] == BIN_M
        assert len({x['input_sha256'] for x in (g, gm, n, mp)}) == 1 and g['bytes'] == 3145728
        h = hist[(i, '2')]
        parity = all(g[k] == h[k] for k in ('archive_sha256', 'probabilities_sha256', 'input_sha256', 'archive_bytes', 'warm_target_bits'))
        assert parity, ('packed16 guard differs from historical guard: stop attribution', i)
        guard_first = (i // 2) % 2 == 0
        assert [c['mode'] for c in reg['cases']] == (['guard_base', 'guard_match'] if guard_first else ['guard_match', 'guard_base'])
        row = {'region': i, 'wave': wave, 'guard_first': guard_first, 'CPU_lane': g['CPU_lane'],
               'packed16_guard_equals_historical_guard': parity,
               'G_archive_B': g['archive_bytes'], 'GM_archive_B': gm['archive_bytes'], 'N_archive_B': n['archive_bytes'], 'M_archive_B': mp['archive_bytes'],
               'G_minus_GM_actual_B': g['archive_bytes'] - gm['archive_bytes'],
               'G_minus_GM_warm_ideal_B': (g['warm_target_bits'] - gm['warm_target_bits']) / 8,
               'G_minus_GM_all_target_ideal_B': (g['all_target_bits'] - gm['all_target_bits']) / 8,
               'N_minus_GM_actual_B': n['archive_bytes'] - gm['archive_bytes'],
               'N_minus_GM_warm_ideal_B': (n['warm_target_bits'] - gm['warm_target_bits']) / 8,
               'N_minus_G_actual_B': n['archive_bytes'] - g['archive_bytes'],
               'N_minus_G_warm_ideal_B': (n['warm_target_bits'] - g['warm_target_bits']) / 8,
               'N_minus_M_actual_B': n['archive_bytes'] - mp['archive_bytes'],
               'interaction_actual_B': g['archive_bytes'] + mp['archive_bytes'] - n['archive_bytes'] - gm['archive_bytes'],
               'interaction_warm_ideal_B': (g['warm_target_bits'] + mp['warm_target_bits'] - n['warm_target_bits'] - gm['warm_target_bits']) / 8}
        for ph in ('encode', 'decode'):
            row[ph + '_G_CPU_s'] = cpu(g, ph); row[ph + '_GM_CPU_s'] = cpu(gm, ph)
            row[ph + '_CPU_saved_s_G_minus_GM'] = cpu(g, ph) - cpu(gm, ph)
            row[ph + '_RSS_saved_KiB_G_minus_GM'] = g[ph]['peak_RSS_KiB'] - gm[ph]['peak_RSS_KiB']
        nb_rows.append(row)
    wall = m['finished'] - m['started']
    nb = {'manifest': str(ps[0].relative_to(R)), 'manifest_sha256': hashlib.sha256(ps[0].read_bytes()).hexdigest(),
          'wall_hours': wall / 3600, 'effective_cores': m['worker_CPU_seconds'] / wall}
    for ph in ('encode', 'decode'):
        d_gf = [r[ph + '_CPU_saved_s_G_minus_GM'] for r in nb_rows if r['guard_first']]
        d_mf = [r[ph + '_CPU_saved_s_G_minus_GM'] for r in nb_rows if not r['guard_first']]
        nb[ph + '_order_balanced_effect_s_per_region'] = statistics.mean(d_gf + d_mf)
        nb[ph + '_position_effect_second_minus_first_s'] = (statistics.mean(d_mf) - statistics.mean(d_gf)) / 2
        nb[ph + '_CPU_reduction_percent'] = 100 * sum(r[ph + '_CPU_saved_s_G_minus_GM'] for r in nb_rows) / sum(r[ph + '_G_CPU_s'] for r in nb_rows)
        nb[ph + '_signs_G_minus_GM'] = {'positive': sum(x > 0 for x in d_gf + d_mf), 'negative': sum(x < 0 for x in d_gf + d_mf)}
    notebooks[wave] = nb; rows += nb_rows
rows.sort(key=lambda r: r['region'])
keys = [k for k in rows[0] if k.endswith(('_B', '_s', '_KiB', '_G_minus_GM')) and not k.endswith('archive_B')]
tot = {k: sum(r[k] for r in rows) for k in keys}
for k in ('G_minus_GM_actual_B', 'G_minus_GM_warm_ideal_B', 'interaction_actual_B', 'interaction_warm_ideal_B', 'N_minus_GM_actual_B'):
    xs = [r[k] for r in rows]; tot[k + '_min_max'] = [min(xs), max(xs)]
    tot[k + '_signs'] = {'positive': sum(x > 0 for x in xs), 'negative': sum(x < 0 for x in xs), 'zero': sum(x == 0 for x in xs)}
for ph in ('encode', 'decode'):
    tot[ph + '_CPU_reduction_percent_G_to_GM'] = 100 * tot[ph + '_CPU_saved_s_G_minus_GM'] / tot[ph + '_G_CPU_s']
    tot[ph + '_RSS_saved_KiB_mean'] = statistics.mean(r[ph + '_RSS_saved_KiB_G_minus_GM'] for r in rows)
    ds = [r[ph + '_CPU_saved_s_G_minus_GM'] for r in rows]
    tot[ph + '_CPU_saved_s_mean_sd'] = [statistics.mean(ds), statistics.stdev(ds)]
    tot[ph + '_CPU_saved_signs'] = {'positive': sum(x > 0 for x in ds), 'negative': sum(x < 0 for x in ds)}
# Freeze: "If timing remains inconsistent, record it as unresolved and use counterbalanced A/B/B/A repeats."
inconsistent = {}
for ph in ('encode', 'decode'):
    sg = tot[ph + '_CPU_saved_signs']; mean, sd = tot[ph + '_CPU_saved_s_mean_sd']
    pos = max(abs(notebooks[w][ph + '_position_effect_second_minus_first_s']) for w in notebooks)
    inconsistent[ph] = {'signs_disagree': sg['positive'] > 0 and sg['negative'] > 0, 'abs_mean_below_sd': abs(mean) < sd,
                        'max_abs_position_effect_s': pos, 'abs_mean_effect_s': abs(mean)}
    inconsistent[ph]['inconsistent'] = inconsistent[ph]['signs_disagree'] or inconsistent[ph]['abs_mean_below_sd']
tot['timing_consistency'] = inconsistent
tot['timing_unresolved_abba_required'] = any(v['inconsistent'] for v in inconsistent.values())
out = {'time': time.time(), 'scope': 'eight 3 MiB confirmation regions; regional histories; no full-history/package claim',
       'regions': rows, 'totals': tot, 'notebooks': notebooks}
(R / 'research_round14_joint_confirmation_analysis_v3.json').write_text(json.dumps(out, indent=2))
print(json.dumps({'totals': tot, 'notebooks': notebooks}, indent=1))
for r in rows:
    print(r['region'], r['wave'], 'G-GM', r['G_minus_GM_actual_B'], round(r['G_minus_GM_warm_ideal_B'], 3), 'N-GM', r['N_minus_GM_actual_B'],
          'N-G', r['N_minus_G_actual_B'], 'I', r['interaction_actual_B'], round(r['interaction_warm_ideal_B'], 3),
          'encG/GM %.0f/%.0f' % (r['encode_G_CPU_s'], r['encode_GM_CPU_s']), 'RSS', r['encode_RSS_saved_KiB_G_minus_GM'])
