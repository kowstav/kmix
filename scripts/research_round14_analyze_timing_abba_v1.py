"""Analysis of the four P1 A/B/B/A timing repeats (freeze research_round14_timing_abba_freeze_v1.md).

Per arm: every per-pair CPU difference (neutral − arm; positive = arm uses less CPU) for
encode and decode separately, per-region means over AB/BA, the order-balanced mean, the
time-position effect (second-run minus first-run CPU), relative reductions, RSS, and
reference-hash parity. Four pairs per arm: descriptive only (no interval). CPU is never
compared across notebooks.
"""

# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
import hashlib, json, statistics, time

R = project_root(__file__)
EV = project_path('research_round14_confirmation_compact_timing-20261010-0504_evidence', base=R)
ARMS = ('prune_word', 'prune_match', 'prune_indirect', 'output_fp32')
out = {'time': time.time(), 'scope': 'same-host counterbalanced timing of unchanged confirmation binaries on regions 8 and 9; '
       'four pairs per arm; descriptive only; regional RSS does not qualify the full stream', 'arms': {}}
for arm in ARMS:
    ps = [p for p in EV.rglob('manifest.json') if json.loads(p.read_text()).get('arm') == arm]
    assert len(ps) == 1, arm
    m = json.loads(ps[0].read_text())
    assert m['status'] == 'COMPLETE_FOUR_LANE_ABBA_TIMING' and m['all_reference_hashes_match'] is True and m['preflight_16KiB'] is False
    assert m['registered_regions'] == [8, 9] and len(m['pairs']) == 4
    assert sorted(p['CPU_lane'] for p in m['pairs']) == m['CPU_lanes']
    for p in m['pairs']:
        for c in p['cases']:
            assert c['exact_independent_inverse'] is True and c['bytes'] == 3145728
    s = m['summary']; a = {'manifest': str(ps[0].relative_to(R)), 'manifest_sha256': hashlib.sha256(ps[0].read_bytes()).hexdigest(),
                           'wall_hours': (m['finished'] - m['started']) / 3600, 'effective_cores': m['effective_cores'],
                           'pairs': [{'region': p['region'], 'order': p['order'], 'CPU_lane': p['CPU_lane'],
                                      'encode_neutral_CPU_s': p['encode_neutral_CPU_s'], 'encode_arm_CPU_s': p['encode_arm_CPU_s'],
                                      'encode_CPU_saved_s': p['encode_CPU_saved_s'], 'decode_neutral_CPU_s': p['decode_neutral_CPU_s'],
                                      'decode_arm_CPU_s': p['decode_arm_CPU_s'], 'decode_CPU_saved_s': p['decode_CPU_saved_s'],
                                      'encode_RSS_saved_KiB': p['encode_RSS_saved_KiB'], 'decode_RSS_saved_KiB': p['decode_RSS_saved_KiB'],
                                      'reference_match': p['reference_match']} for p in m['pairs']]}
    for ph in ('encode', 'decode'):
        d = s[ph]['per_pair_CPU_saved_s']; base = [p[ph + '_neutral_CPU_s'] for p in m['pairs']]
        a[ph] = {'per_pair_CPU_saved_s': d, 'order_balanced_mean_CPU_saved_s': s[ph]['order_balanced_mean_CPU_saved_s'],
                 'per_region_mean_CPU_saved_s': s[ph]['per_region_mean_CPU_saved_s'],
                 'CPU_reduction_percent': s[ph]['CPU_reduction_percent'],
                 'position_effect_second_minus_first_s': s[ph]['position_effect_second_minus_first_s_mean'],
                 'per_pair_reduction_percent': [100 * x / b for x, b in zip(d, base)],
                 'signs': {'positive': sum(x > 0 for x in d), 'negative': sum(x < 0 for x in d)},
                 'min_max_CPU_saved_s': [min(d), max(d)]}
        a[ph]['all_four_pairs_same_sign'] = a[ph]['signs']['positive'] in (0, 4)
    a['RSS_saved_KiB_mean'] = statistics.mean(p['encode_RSS_saved_KiB'] for p in m['pairs'])
    out['arms'][arm] = a
(project_path('research_round14_timing_abba_analysis_v1.json', base=R)).write_text(json.dumps(out, indent=2))
for arm, a in out['arms'].items():
    print(arm, 'cores %.3f wall %.2fh' % (a['effective_cores'], a['wall_hours']), 'RSS saved %.0f KiB' % a['RSS_saved_KiB_mean'])
    for ph in ('encode', 'decode'):
        x = a[ph]
        print('  %s: per-pair saved s %s | balanced %+.1f s (%+.2f%%) | per-region %s | position %+.1f s | same sign %s' % (
            ph, [round(v, 1) for v in x['per_pair_CPU_saved_s']], x['order_balanced_mean_CPU_saved_s'], x['CPU_reduction_percent'],
            {k: round(v, 1) for k, v in x['per_region_mean_CPU_saved_s'].items()}, x['position_effect_second_minus_first_s'], x['all_four_pairs_same_sign']))
