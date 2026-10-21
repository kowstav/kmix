"""Eight-region component confirmation (A=8,10,12,14 + B=9,11,13,15) and joint
confirmation A (guard G vs guard+match-pruning GM on 8,10,12,14).

Signed effects are baseline minus candidate. Eight clusters are below the
ten-cluster bootstrap gate, so only per-region values, sums and min/max are
reported; no confidence interval is computed. CPU is compared only within one
notebook/host (matched pairs). Existing component N/M rows are used for the
guard x match BYTE interaction only, never for CPU.
"""
from pathlib import Path
import hashlib, json, statistics, time

R = Path(__file__).resolve().parent
EV = {'a': R / 'research_round14_confirmation_compact_a-20261009-1734_evidence',
      'b': R / 'research_round14_confirmation_compact_b-20261009-2328_evidence'}
JA = R / 'research_round14_confirmation_compact_joint-a-20261009-2325_evidence'
BIN = {'neutral': '30b539b3ec2cd0a2adf51d3103f2643d113022cce2c7fb17b9828b6f61e10fda',
       'prune_word': 'c2ba7d4c10912e9bac9d53b3e890a1cb458e0396eb3c6c3d70c681800168e56d',
       'prune_match': 'cf8fc836f7225f2b25b48d76ffb5ce3bf0682f91549082a1d4ba0353755c8a6e',
       'prune_indirect': 'c6aca330ce814aeafd7115a82bcea43f59a8a4dd77c5f7d341ba18513ca9281b',
       'output_fp32': '470d4f8c66e07910d92b18f80d1d73ef450f23d0a77e1eda6e6c3fa27a108565'}
ARMS = ('prune_word', 'prune_match', 'prune_indirect', 'output_fp32')


def cpu(case, phase):
    return case[phase]['CPU_user_seconds'] + case[phase]['CPU_system_seconds']


def sha_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


# Historical native confirmation (pinned neutral and mode-2 guard) for regions 8..15.
hist = {}
for p in (R / 'research_round14_batch_evidence').glob('hutter-r14-native-confirmation-*/native-confirmation/manifest.json'):
    for r in json.loads(p.read_text())['regions']:
        for c in r['cases']:
            hist[(r['region'], str(c['mode']))] = c
assert sorted({k[0] for k in hist}) == list(range(8, 16))

dev = json.loads((R / 'research_round14_native_wave_analysis_v1.json').read_text())['native']
result = {'time': time.time(),
          'scope': 'eight 3 MiB regional confirmation histories per arm (2 MiB warmup, last 1 MiB warm); '
                   'joint confirmation A only (4 regions); no population interval, full-history or package claim',
          'evidence': {}, 'components': {}, 'joint_confirmation_a': {}}
for wave, d in EV.items():
    result['evidence']['component_' + wave] = sorted(str(p.relative_to(R)) for p in d.rglob('manifest.json'))

neutral_seen = {}
for arm in ARMS:
    rows, notebooks = [], {}
    for wave, d in EV.items():
        ps = [p for p in d.rglob('manifest.json') if json.loads(p.read_text()).get('arm') == arm]
        assert len(ps) == 1, (arm, wave, ps)
        m = json.loads(ps[0].read_text())
        ids = {8, 10, 12, 14} if wave == 'a' else {9, 11, 13, 15}
        assert m['status'] == 'COMPLETE_FOUR_NATIVE_PAIRS' and m['run_label'] == 'confirmation_' + wave
        assert {r['region'] for r in m['regions']} == ids
        wall = m['finished'] - m['started']
        notebook = {'manifest': str(ps[0].relative_to(R)), 'manifest_sha256': sha_file(ps[0]),
                    'wall_hours': wall / 3600, 'worker_CPU_seconds': m['worker_CPU_seconds'],
                    'effective_cores': m['worker_CPU_seconds'] / wall}
        nb_rows = []
        for reg in sorted(m['regions'], key=lambda r: r['region']):
            i = reg['region']; by = {c['mode']: c for c in reg['cases']}; n, c = by['neutral'], by[arm]
            assert n['exact_independent_inverse'] is True and c['exact_independent_inverse'] is True
            assert n['input_sha256'] == c['input_sha256'] and n['bytes'] == c['bytes'] == 3145728
            assert n['binary_sha256'] == BIN['neutral'] and c['binary_sha256'] == BIN[arm]
            ref = hist[(i, 'pinned')]
            parity = all(n[k] == ref[k] for k in ('archive_sha256', 'probabilities_sha256', 'input_sha256', 'warm_target_bits'))
            assert parity, ('neutral differs from historical pinned confirmation; stop attribution', arm, i)
            key = (n['archive_sha256'], n['probabilities_sha256'])
            assert neutral_seen.setdefault(i, key) == key, 'neutral differs across notebooks'
            baseline_first = (i // 2) % 2 == 0
            assert [x['mode'] for x in reg['cases']] == (['neutral', arm] if baseline_first else [arm, 'neutral'])
            row = {'region': i, 'wave': wave, 'baseline_first': baseline_first, 'CPU_lane': n['CPU_lane'],
                   'neutral_matches_historical_pinned': parity,
                   'baseline_archive_B': n['archive_bytes'], 'candidate_archive_B': c['archive_bytes'],
                   'actual_gain_B': n['archive_bytes'] - c['archive_bytes'],
                   'warm_gain_ideal_B': (n['warm_target_bits'] - c['warm_target_bits']) / 8,
                   'all_target_gain_ideal_B': (n['all_target_bits'] - c['all_target_bits']) / 8}
            for phase in ('encode', 'decode'):
                row[phase + '_baseline_CPU_s'] = cpu(n, phase); row[phase + '_candidate_CPU_s'] = cpu(c, phase)
                row[phase + '_CPU_saved_s'] = cpu(n, phase) - cpu(c, phase)
                row[phase + '_RSS_saved_KiB'] = n[phase]['peak_RSS_KiB'] - c[phase]['peak_RSS_KiB']
            nb_rows.append(row)
        # Order-balanced decomposition inside one host: d = delta -/+ p (p = second-run minus first-run CPU).
        for phase in ('encode', 'decode'):
            d_bf = [r[phase + '_CPU_saved_s'] for r in nb_rows if r['baseline_first']]
            d_cf = [r[phase + '_CPU_saved_s'] for r in nb_rows if not r['baseline_first']]
            assert len(d_bf) == len(d_cf) == 2
            notebook[phase + '_order_balanced_arm_effect_s_per_region'] = statistics.mean(d_bf + d_cf)
            notebook[phase + '_position_effect_second_minus_first_s'] = (statistics.mean(d_cf) - statistics.mean(d_bf)) / 2
        notebooks[wave] = notebook; rows += nb_rows
    rows.sort(key=lambda r: r['region'])
    t = {k: sum(r[k] for r in rows) for k in rows[0] if k.endswith(('_B', '_s', '_KiB')) and not k.startswith(('baseline_archive', 'candidate_archive'))}
    t['baseline_archive_B'] = sum(r['baseline_archive_B'] for r in rows)
    for phase in ('encode', 'decode'):
        t[phase + '_CPU_reduction_percent'] = 100 * t[phase + '_CPU_saved_s'] / t[phase + '_baseline_CPU_s']
        t[phase + '_RSS_saved_KiB_mean'] = statistics.mean(r[phase + '_RSS_saved_KiB'] for r in rows)
        for wave in 'ab':
            sel = [r for r in rows if r['wave'] == wave]
            t[phase + '_CPU_reduction_percent_wave_' + wave] = 100 * sum(r[phase + '_CPU_saved_s'] for r in sel) / sum(r[phase + '_baseline_CPU_s'] for r in sel)
        ds = [r[phase + '_CPU_saved_s'] for r in rows]
        t[phase + '_CPU_saved_s_min_max'] = [min(ds), max(ds)]
        t[phase + '_CPU_saved_sign_counts'] = {'positive': sum(x > 0 for x in ds), 'negative': sum(x < 0 for x in ds)}
        t[phase + '_CPU_saved_s_mean_and_sd'] = [statistics.mean(ds), statistics.stdev(ds)]
    for k in ('actual_gain_B', 'warm_gain_ideal_B', 'all_target_gain_ideal_B'):
        xs = [r[k] for r in rows]
        t[k + '_min_max'] = [min(xs), max(xs)]
        t[k + '_sign_counts'] = {'positive': sum(x > 0 for x in xs), 'negative': sum(x < 0 for x in xs), 'zero': sum(x == 0 for x in xs)}
    # Registered timing-repeat rule (written before the B wave was opened): a development-proposed
    # CPU gain (positive development reduction) that, over eight confirmation pairs, has disagreeing
    # signs or |mean| below one paired standard deviation is "comparable with paired variability".
    rule = {}
    for phase in ('encode', 'decode'):
        dev_pct = dev[arm]['totals'][phase + '_CPU_saved_percent']
        mean, sd = t[phase + '_CPU_saved_s_mean_and_sd']; sc = t[phase + '_CPU_saved_sign_counts']
        rule[phase] = {'development_reduction_percent': dev_pct, 'proposed_gain': dev_pct > 0,
                       'signs_disagree': sc['positive'] > 0 and sc['negative'] > 0, 'abs_mean_below_sd': abs(mean) < sd}
        rule[phase]['repeat_required'] = rule[phase]['proposed_gain'] and (rule[phase]['signs_disagree'] or rule[phase]['abs_mean_below_sd'])
    t['timing_repeat_rule'] = rule
    t['timing_repeat_required'] = any(v['repeat_required'] for v in rule.values())
    result['components'][arm] = {'regions': rows, 'totals': t, 'notebooks': notebooks,
                                 'development_totals': {k: dev[arm]['totals'][k] for k in ('actual_gain_B', 'warm_gain_ideal_B', 'encode_CPU_saved_percent', 'decode_CPU_saved_percent')}}

# Joint confirmation A: G vs GM, guard parity with the historical mode-2 guard, byte interaction with component N/M.
ps = list(JA.rglob('manifest.json')); assert len(ps) == 1
m = json.loads(ps[0].read_text())
assert m['status'] == 'COMPLETE_FOUR_NATIVE_GUARD_MATCH_PAIRS' and m['run_label'] == 'confirmation_a'
assert sorted(r['region'] for r in m['regions']) == [8, 10, 12, 14] == m['registered_regions']
compA = {}
for p in EV['a'].rglob('manifest.json'):
    mm = json.loads(p.read_text())
    for r in mm['regions']:
        for c in r['cases']:
            compA[(r['region'], c['mode'])] = c
rows = []
for reg in sorted(m['regions'], key=lambda r: r['region']):
    i = reg['region']; by = {c['mode']: c for c in reg['cases']}; g, gm = by['guard_base'], by['guard_match']
    n, mp = compA[(i, 'neutral')], compA[(i, 'prune_match')]
    assert g['exact_independent_inverse'] is True and gm['exact_independent_inverse'] is True
    assert len({x['input_sha256'] for x in (g, gm, n, mp)}) == 1
    assert n['binary_sha256'] == BIN['neutral'] and mp['binary_sha256'] == BIN['prune_match']
    h = hist[(i, '2')]
    guard_parity = all(g[k] == h[k] for k in ('archive_sha256', 'probabilities_sha256', 'input_sha256', 'archive_bytes', 'warm_target_bits'))
    assert guard_parity, ('guard baseline differs from historical guard', i)
    assert g['bytes'] == 3145728 and g['binary_sha256'] != gm['binary_sha256']
    guard_first = (i // 2) % 2 == 0
    row = {'region': i, 'guard_first': guard_first, 'CPU_lane': g['CPU_lane'], 'guard_matches_historical_mode2': guard_parity,
           'guard_marginal_actual_B_G_minus_GM': g['archive_bytes'] - gm['archive_bytes'],
           'guard_marginal_warm_ideal_B_G_minus_GM': (g['warm_target_bits'] - gm['warm_target_bits']) / 8,
           'guard_marginal_all_target_ideal_B_G_minus_GM': (g['all_target_bits'] - gm['all_target_bits']) / 8,
           'joint_vs_neutral_actual_B_N_minus_GM': n['archive_bytes'] - gm['archive_bytes'],
           'joint_vs_neutral_warm_ideal_B_N_minus_GM': (n['warm_target_bits'] - gm['warm_target_bits']) / 8,
           'match_marginal_without_guard_actual_B_N_minus_M': n['archive_bytes'] - mp['archive_bytes'],
           'interaction_actual_B': g['archive_bytes'] + mp['archive_bytes'] - n['archive_bytes'] - gm['archive_bytes'],
           'interaction_warm_ideal_B': (g['warm_target_bits'] + mp['warm_target_bits'] - n['warm_target_bits'] - gm['warm_target_bits']) / 8,
           'guard_binary_sha256': g['binary_sha256'], 'guard_match_binary_sha256': gm['binary_sha256']}
    for phase in ('encode', 'decode'):
        row[phase + '_G_CPU_s'] = cpu(g, phase); row[phase + '_GM_CPU_s'] = cpu(gm, phase)
        row[phase + '_CPU_saved_s_G_minus_GM'] = cpu(g, phase) - cpu(gm, phase)
        row[phase + '_RSS_saved_KiB_G_minus_GM'] = g[phase]['peak_RSS_KiB'] - gm[phase]['peak_RSS_KiB']
    rows.append(row)
t = {k: sum(r[k] for r in rows) for k in rows[0] if k.endswith(('_B', '_s', '_KiB')) or '_B_' in k or k.endswith('_GM')}
t = {k: v for k, v in t.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
wall = m['finished'] - m['started']
nb = {'manifest': str(ps[0].relative_to(R)), 'manifest_sha256': sha_file(ps[0]), 'wall_hours': wall / 3600,
      'effective_cores': m['worker_CPU_seconds'] / wall}
for phase in ('encode', 'decode'):
    d_gf = [r[phase + '_CPU_saved_s_G_minus_GM'] for r in rows if r['guard_first']]
    d_mf = [r[phase + '_CPU_saved_s_G_minus_GM'] for r in rows if not r['guard_first']]
    nb[phase + '_order_balanced_effect_s_per_region'] = statistics.mean(d_gf + d_mf)
    nb[phase + '_position_effect_second_minus_first_s'] = (statistics.mean(d_mf) - statistics.mean(d_gf)) / 2
    t[phase + '_CPU_reduction_percent_G_to_GM'] = 100 * sum(r[phase + '_CPU_saved_s_G_minus_GM'] for r in rows) / sum(r[phase + '_G_CPU_s'] for r in rows)
    t[phase + '_RSS_saved_KiB_mean'] = statistics.mean(r[phase + '_RSS_saved_KiB_G_minus_GM'] for r in rows)
result['joint_confirmation_a'] = {'regions': rows, 'totals': t, 'notebook': nb,
                                  'note': 'B (9,11,13,15) submitted 9 Oct 23:27 UTC; eight-region joint totals pending'}
(R / 'research_round14_confirm_ab_joint_a_analysis_v2.json').write_text(json.dumps(result, indent=2))

summary = {'components': {a: {k: v for k, v in result['components'][a]['totals'].items()} | {'notebooks': result['components'][a]['notebooks']}
                          for a in ARMS}, 'joint_a_totals': t, 'joint_a_notebook': nb}
print(json.dumps(summary, indent=1))
