"""P2 live probe: exact-storage parity, startup-inclusive CPU and peak RSS (16 KiB).

Run in the live Kaggle session (no batch slot): python3 this.py.dat
Four pinned lanes, each an A/B/B/A sequence on its own CPU with the unchanged
`cpu_round13_native.archive_case` harness (separate encoder and independent decoder,
whole-process rusage including startup, Q16 trace) on the first 16 KiB of canonical
region 0 (input SHA-256 87ad632a...). Every archive/Q16 hash must equal the stored
16 KiB references; any difference is a new candidate, not an implementation saving.
Regional/16 KiB peak RSS measures fixed-allocation increments only; it does NOT
qualify the full-stream peak (historical full run 9,765,024 KiB).
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib, io, json, multiprocessing as mp, os, resource, shutil, statistics, sys, time, traceback, zipfile

W = Path('/kaggle/working/hp_round14')
OUTD = W / 'p2_startup_rss_probe_v1'
ROOT = Path('/root/r14_p2_probe_v1')
SRC_SHA = 'c792a9fbb6151b0b7c9366517a21413c038188620ca65b6b4155e41b58cbba2c'  # frozen timing source bundle (unchanged harness)
BINS = {  # name -> (path, sha256) from guard_storage_build_v2.json and guard_match_pipeline_v1.json
    'neutral_raw': ('guard_storage_binaries_v2/cmix_neutral_raw', '30b539b3ec2cd0a2adf51d3103f2643d113022cce2c7fb17b9828b6f61e10fda'),
    'neutral_raw_upx': ('guard_storage_binaries_v2/cmix_neutral_raw_upx', '21546f55acc73121d22342dac950f8819f8d9293fb6e03af07e2180c14e07539'),
    'guard_raw': ('guard_storage_binaries_v2/cmix_guard_raw', '752a774c0455c50ac1799ccf029a7daa89499566165b8c492251b4d45841aa8e'),
    'guard_packed16': ('guard_storage_binaries_v2/cmix_guard_packed16', '5f6e0c7b8be11894e979033a94206b7523796656be590794d78d81e9739cb657'),
    'guard_packed16_upx': ('guard_storage_binaries_v2/cmix_guard_packed16_upx', '8e562a69774ec852671cb3176095336a692d0514f1ecaed561483ba2a3f64e53'),
    'joint_upx': (None, 'd484b05cfe72029595b4b1c782ba24485004fee3c710dff0a185297279c1858c'),
}
REF = {  # stored 16 KiB region-0 references (archive, Q16)
    'neutral': ('1c2c2188fd68d6ad', '5aa4693d6aaff622'),
    'guard': ('ed0adaa890056164', '9e8174a1290636bb'),
    'joint': ('d5001d578a5c6cab', '275f430c90d13751'),
}
FAMILY = {'neutral_raw': 'neutral', 'neutral_raw_upx': 'neutral', 'guard_raw': 'guard', 'guard_packed16': 'guard',
          'guard_packed16_upx': 'guard', 'joint_upx': 'joint'}
LANES = [('neutral_raw', 'guard_packed16'), ('guard_raw', 'guard_packed16'),
         ('neutral_raw_upx', 'guard_packed16_upx'), ('guard_packed16_upx', 'joint_upx')]
native = None; lanes_mod = None


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''): h.update(b)
    return h.hexdigest()


def lane(task):
    k, (a, b) = task
    rows = []
    for j, mode in enumerate((a, b, b, a)):
        d = ROOT / f'lane{k}' / f'run{j}_{mode}'; d.mkdir(parents=True)
        native.ROOT = d; native.OUT = d / 'out'; native.OUT.mkdir()
        shutil.copyfile(ROOT / 'bin' / ('cmix_' + mode), d / ('cmix_head_' + mode)); (d / ('cmix_head_' + mode)).chmod(0o700)
        t0 = time.time(); r = native.archive_case(0, mode, preflight=True, expected_bytes=16384)
        r['start_unix'] = t0; r['end_unix'] = time.time(); r['sequence_position'] = j
        ref = REF[FAMILY[mode]]
        r['reference_match'] = r['archive_sha256'].startswith(ref[0]) and r['probabilities_sha256'].startswith(ref[1])
        rows.append(r)
    out = {'lane_task': k, 'pair': [a, b], 'CPU_lane': lanes_mod.LANE_CPU, 'runs': rows}
    for phase in ('encode', 'decode'):
        def c(r): return r[phase]['CPU_user_seconds'] + r[phase]['CPU_system_seconds']
        A = [c(r) for r in rows if r['mode'] == a]; B = [c(r) for r in rows if r['mode'] == b]
        # sequence A,B,B,A: adjacent pairs (pos0,pos1) and (pos3,pos2)
        out[phase + '_CPU_A_minus_B_s_per_repeat'] = [A[0] - B[0], A[1] - B[1]]
        out[phase + '_CPU_mean_A_minus_B_s'] = statistics.mean(A) - statistics.mean(B)
        out[phase + '_peak_RSS_KiB_A'] = [r[phase]['peak_RSS_KiB'] for r in rows if r['mode'] == a]
        out[phase + '_peak_RSS_KiB_B'] = [r[phase]['peak_RSS_KiB'] for r in rows if r['mode'] == b]
    return out


def main():
    global native, lanes_mod
    assert not OUTD.exists() and not ROOT.exists(); OUTD.mkdir(); ROOT.mkdir()
    M = {'status': 'VERIFYING', 'started': time.time(), 'lanes': LANES, 'design': 'per lane A/B/B/A on one pinned CPU, 16 KiB canonical region 0',
         'pairs': [], 'deletions': [], 'GPU': False, 'paid_usd': 0,
         'scope': 'startup-inclusive 16 KiB CPU and fixed-allocation RSS; no full-stream RSS qualification'}
    def save(): (OUTD / 'manifest.json').write_text(json.dumps(M, indent=2))
    try:
        save()
        raw = (W / 'sources_timing_abba_v9.zip.dat').read_bytes(); assert hashlib.sha256(raw).hexdigest() == SRC_SHA
        code = ROOT / 'code'
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for e in json.loads(z.read('source_manifest.json')):
                p = (code / e['path']).resolve(); assert p.is_relative_to(code); b = z.read(e['path'])
                assert hashlib.sha256(b).hexdigest() == e['sha256']; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b)
        sys.path.insert(0, str(code))
        from hutter_research import cpu_round13_native as n, cpu_round13_jobs as lj
        native, lanes_mod = n, lj
        jm = list((W / 'guard_match_binaries_v1').glob('*'))
        joint = [p for p in jm if p.is_file() and sha(p) == BINS['joint_upx'][1]]
        assert len(joint) == 1, [p.name for p in jm]
        (ROOT / 'bin').mkdir()
        for name, (rel, digest) in BINS.items():
            p = joint[0] if name == 'joint_upx' else W / rel
            assert sha(p) == digest, name; shutil.copyfile(p, ROOT / 'bin' / ('cmix_' + name))
        M['binaries'] = {k: {'sha256': v[1], 'bytes': (ROOT / 'bin' / ('cmix_' + k)).stat().st_size} for k, v in BINS.items()}
        asset = Path('/root/r14_assets/r13'); meta = json.loads((asset / 'r13_assets.json').read_text())
        for name, r in meta['files'].items():
            if name.endswith('.bin') or name in ('original.tfwc3', 'english.dic', 'vocab.bm'):
                assert (asset / name).stat().st_size == r['bytes'] and sha(asset / name) == r['sha256'], name
        n.ASSET = asset; n.DEADLINE = time.monotonic() + 3 * 3600
        cpus = sorted(os.sched_getaffinity(0))[:4]; assert len(cpus) == 4
        ctx = mp.get_context('fork'); q = ctx.Queue()
        for c in cpus: q.put(c)
        before = resource.getrusage(resource.RUSAGE_CHILDREN); M['status'] = 'RUNNING_FOUR_LANE_ABBA'; save()
        with ProcessPoolExecutor(4, mp_context=ctx, initializer=lj.initialize_lane, initargs=(q,)) as pool:
            for f in as_completed([pool.submit(lane, t) for t in enumerate(LANES)]):
                M['pairs'].append(f.result()); save()
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        M['pairs'].sort(key=lambda p: p['lane_task'])
        M['finished'] = time.time(); M['worker_CPU_seconds'] = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
        M['effective_cores'] = M['worker_CPU_seconds'] / (M['finished'] - M['started'])
        ok = all(r['reference_match'] for p in M['pairs'] for r in p['runs'])
        rss = {}
        for p in M['pairs']:
            for r in p['runs']:
                rss.setdefault(r['mode'], []).append(r['encode']['peak_RSS_KiB'])
        M['encode_peak_RSS_KiB_by_binary'] = rss
        M['all_reference_hashes_match'] = ok
        M['status'] = 'COMPLETE_EXACT_PARITY_STARTUP_RSS_PROBE' if ok else 'COMPLETE_PARITY_MISMATCH_NEW_CANDIDATE'
        save(); print(json.dumps({'status': M['status'], 'effective_cores': M['effective_cores'], 'rss': rss}))
    except BaseException as e:
        M.update(status='FAIL_PRESERVED', error=repr(e), traceback=traceback.format_exc(), finished=time.time()); save(); raise


if __name__ == '__main__':
    main()
