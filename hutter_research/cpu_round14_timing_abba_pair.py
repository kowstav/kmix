"""Counterbalanced A/B/B/A CPU timing repeat for one frozen binary pair (generalized).

Same registered design as cpu_round14_timing_abba (frozen v9), parameterized by the
asset manifest and the two mode names, so pairs other than neutral-vs-arm (here the
joint guard G vs guard+match-pruning GM) use an identical code path. Four pinned lanes
= two registered regions x orders AB/BA; per region the four runs form A/B/B/A in time.
Every run is the unchanged `cpu_round13_native.archive_case` (separate encoder and
independent decoder, whole-process rusage including startup, exact inverse, Q16
trace); lanes use private ROOT/OUT so repeated labels never collide. Archive/Q16
hashes are compared with confirmation references; a mismatch stops attribution but
every run is kept. No bytes, rates, tables, binaries or flags differ from the jobs
whose timing is being repeated.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import json, multiprocessing as mp, os, resource, shutil, statistics, time, traceback
from . import cpu_round13_native as native
from . import cpu_round13_jobs as lanes
from .cpu_round13_jobs import atomic_json, initialize_lane, sha

PAIRS = {  # label -> (asset manifest, gate key, gate value, baseline mode, candidate mode)
    'guard_vs_guard_match': ('guard_match_assets.json', 'gate', 'PASS_FOUR_NATIVE_COMBINED_INVERSES_AND_PACKED_GUARD_PARITY',
                             'guard_base', 'guard_match'),
}
A = B = None
BASE_ROOT = BASE_OUT = BIN = None
REFERENCE = None
PREFLIGHT = False


def lane_pair(task):
    k, region, order = task
    modes = [A, B] if order == 'AB' else [B, A]
    tag = f'lane{k}_r{region:02}_{order}'
    native.ROOT = BASE_ROOT / tag; native.ROOT.mkdir()
    native.OUT = BASE_OUT / tag; native.OUT.mkdir()
    for name in (A, B):
        p = native.ROOT / ('cmix_head_' + name); shutil.copyfile(BIN / ('cmix_' + name), p); p.chmod(0o700)
    rows, stamps = [], []
    for mode in modes:
        t0 = time.time()
        if PREFLIGHT:
            row = native.archive_case(region, mode, preflight=True, expected_bytes=16384)
        else:
            row = native.archive_case(region, mode, expected_bytes=3145728)
        rows.append(row); stamps.append({'mode': mode, 'start_unix': t0, 'end_unix': time.time()})
    by = {r['mode']: r for r in rows}
    out = {'lane_task': k, 'region': region, 'order': order, 'CPU_lane': lanes.LANE_CPU,
           'affinity': sorted(os.sched_getaffinity(0)), 'worker_pid': os.getpid(), 'timestamps': stamps,
           'cases': rows, 'reference_match': {}}
    assert len({r['input_sha256'] for r in rows}) == 1
    for mode in (A, B):
        ref = REFERENCE[str(region)][mode]
        out['reference_match'][mode] = all(by[mode][key] == ref[key] for key in ('archive_sha256', 'probabilities_sha256', 'archive_bytes'))
    for phase in ('encode', 'decode'):
        def cpu(r): return r[phase]['CPU_user_seconds'] + r[phase]['CPU_system_seconds']
        out[phase + '_CPU_saved_s'] = cpu(by[A]) - cpu(by[B])
        out[phase + '_wall_saved_s'] = by[A][phase]['wall_seconds'] - by[B][phase]['wall_seconds']
        out[phase + '_RSS_saved_KiB'] = by[A][phase]['peak_RSS_KiB'] - by[B][phase]['peak_RSS_KiB']
        out[phase + '_baseline_CPU_s'] = cpu(by[A]); out[phase + '_candidate_CPU_s'] = cpu(by[B])
    out['actual_gain_B'] = by[A]['archive_bytes'] - by[B]['archive_bytes']
    out['warm_gain_ideal_B'] = (by[A]['warm_target_bits'] - by[B]['warm_target_bits']) / 8
    return out


def summarize(pairs):
    s = {}
    for phase in ('encode', 'decode'):
        d = [p[phase + '_CPU_saved_s'] for p in pairs]
        base = sum(p[phase + '_baseline_CPU_s'] for p in pairs)
        second_minus_first = []
        for p in pairs:
            a, b = p[phase + '_baseline_CPU_s'], p[phase + '_candidate_CPU_s']
            second_minus_first.append((b - a) if p['order'] == 'AB' else (a - b))
        s[phase] = {'per_pair_CPU_saved_s': d, 'order_balanced_mean_CPU_saved_s': statistics.mean(d),
                    'CPU_reduction_percent': 100 * sum(d) / base,
                    'per_region_mean_CPU_saved_s': {str(r): statistics.mean([p[phase + '_CPU_saved_s'] for p in pairs if p['region'] == r])
                                                   for r in sorted({p['region'] for p in pairs})},
                    'position_effect_second_minus_first_s_mean': statistics.mean(second_minus_first),
                    'per_pair_wall_saved_s': [p[phase + '_wall_saved_s'] for p in pairs],
                    'per_pair_RSS_saved_KiB': [p[phase + '_RSS_saved_KiB'] for p in pairs]}
    return s


def main(label, regions=(8, 9), reference=None, preflight=False, asset_dir=None, head_dir=None, out_dir=None, root_dir=None):
    global A, B, BASE_ROOT, BASE_OUT, BIN, REFERENCE, PREFLIGHT
    manifest_name, gate_key, gate_value, A, B = PAIRS[label]; PREFLIGHT = bool(preflight)
    regions = tuple(regions); assert len(regions) == 2
    assert regions == ((0, 0) if PREFLIGHT else (8, 9)), 'registered regions: 8 and 9 (lowest of each confirmation half)'
    REFERENCE = reference; assert all(str(r) in REFERENCE and set(REFERENCE[str(r)]) >= {A, B} for r in regions)
    if asset_dir is None:
        a = list(Path('/kaggle/input').rglob('r13_assets.json')); b = list(Path('/kaggle/input').rglob(manifest_name))
    else:
        a = [Path(asset_dir) / 'r13_assets.json']; b = [Path(head_dir) / manifest_name]
    assert len(a) == len(b) == 1
    native.ASSET = a[0].parent; head = b[0].parent
    suffix = '_preflight' if PREFLIGHT else ''
    BASE_ROOT = Path(root_dir or '/root') / ('r14_timing_abba_' + label + suffix); BASE_ROOT.mkdir()
    BASE_OUT = Path(out_dir or '/kaggle/working') / ('timing-abba-' + label + suffix); BASE_OUT.mkdir()
    native.DEADLINE = time.monotonic() + 10.3 * 3600
    M = {'status': 'VERIFYING_ASSETS', 'started': time.time(), 'pair_label': label, 'baseline_mode': A, 'candidate_mode': B,
         'registered_regions': list(regions), 'preflight_16KiB': PREFLIGHT,
         'design': 'four pinned lanes = 2 regions x orders AB/BA; per region A/B/B/A',
         'reference': REFERENCE, 'pairs': [], 'workers': 4, 'deletions': [], 'GPU': False, 'paid_usd': 0,
         'scope': 'matched same-host CPU timing of unchanged confirmation binaries; regional peak RSS does not qualify the full stream'}
    def save(): atomic_json(BASE_OUT / 'manifest.json', M)
    try:
        save(); meta = json.loads(b[0].read_text())
        assert meta[gate_key] == gate_value
        for manifest in (a[0], b[0]):
            for n, r in json.loads(manifest.read_text())['files'].items():
                p = manifest.parent / n; assert p.stat().st_size == r['bytes'] and sha(p) == r['sha256'], n
        BIN = BASE_ROOT / 'bin'; BIN.mkdir()
        for name in (A, B):
            shutil.copyfile(head / ('cmix_' + name), BIN / ('cmix_' + name))
        M['binary_sha256'] = {name: sha(BIN / ('cmix_' + name)) for name in (A, B)}
        M['asset_manifest_sha256'] = sha(b[0]); M['asset_source_sha256'] = meta.get('source_sha256')
        cpus = sorted(os.sched_getaffinity(0))[:4]; assert len(cpus) == 4; M['CPU_lanes'] = cpus
        ctx = mp.get_context('fork'); q = ctx.Queue()
        for c in cpus: q.put(c)
        tasks = [(k, r, o) for k, (r, o) in enumerate((r, o) for r in regions for o in ('AB', 'BA'))]
        M['tasks'] = tasks
        before = resource.getrusage(resource.RUSAGE_CHILDREN); M['status'] = 'FOUR_LANE_ABBA_TIMING'; save()
        with ProcessPoolExecutor(4, mp_context=ctx, initializer=initialize_lane, initargs=(q,)) as pool:
            for f in as_completed([pool.submit(lane_pair, t) for t in tasks]):
                M['pairs'].append(f.result()); save()
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        M['finished'] = time.time()
        M['worker_CPU_seconds'] = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
        M['effective_cores'] = M['worker_CPU_seconds'] / (M['finished'] - M['started'])
        M['pairs'].sort(key=lambda p: p['lane_task'])
        assert sorted(p['CPU_lane'] for p in M['pairs']) == cpus, 'lanes were not one per pinned CPU'
        M['summary'] = summarize(M['pairs'])
        ok = all(all(p['reference_match'].values()) for p in M['pairs'])
        M['all_reference_hashes_match'] = ok
        M['status'] = ('COMPLETE_FOUR_LANE_ABBA_TIMING' if ok else 'COMPLETE_TIMING_REFERENCE_MISMATCH_STOP_ATTRIBUTION')
        if PREFLIGHT:
            M['status'] = 'PASS_16KIB_PREFLIGHT_REFERENCE_PARITY' if ok else 'FAIL_16KIB_PREFLIGHT_REFERENCE_MISMATCH'
        save()
        return M
    except BaseException as e:
        M.update(status='FAIL_PRESERVED', error=repr(e), traceback=traceback.format_exc(), finished=time.time()); save(); raise
