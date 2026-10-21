"""P4 lexical structural experts: native regional archives on PHDA9 tail regions.

Modes (HP_R14_STRUCTX build flag): 0 = pinned neutral binary (identical to R14 neutral
30b539b3...); 1 = topology-matched neutral expert (extra input 0.5, extra mixer context 0);
2 = joint predictor (experts with true keys); 3 = wrong-key control. Every case is a
separate encoder process plus an independent decoder process, with an exact inverse, a
Q16 trace, whole-process rusage, warm (last 1 MiB) and all-target ideal cost. The logic
is the same as cpu_round13_native.archive_case, plus the lab-only owner list for
interlanguage regions (LAB_IW_OWNERS / LAB_IW_BLOCK0), which the causal parser built over
the preceding stream; encoder and decoder receive the same file. Regions are fixed-rule 3 MiB
windows (2 MiB warmup) inside the revision-record and interlanguage tails: earlier record
blocks are development and later blocks are confirmation; windows never overlap.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import gzip, hashlib, json, multiprocessing as mp, os, resource, shutil, subprocess, time, traceback
import numpy as np
from .cpu_round13_jobs import atomic_json, initialize_lane, sha
from . import cpu_round13_jobs as lanes

ASSET = BIN = OUT = ROOT = None
DEADLINE = None


def run(args, work, env, label):
    start = time.monotonic()
    with (work / (label + '.log')).open('xb') as f:
        p = subprocess.Popen(args, cwd=work, env=env, stdout=f, stderr=subprocess.STDOUT)
        stop = None
        while True:
            pid, status, u = os.wait4(p.pid, os.WNOHANG)
            if pid: p.returncode = os.waitstatus_to_exitcode(status); break
            if time.monotonic() > DEADLINE: stop = 'declared notebook deadline'; p.terminate()
            time.sleep(.5)
    return {'exit': p.returncode, 'wall_seconds': time.monotonic() - start, 'CPU_user_seconds': u.ru_utime,
            'CPU_system_seconds': u.ru_stime, 'peak_RSS_KiB': u.ru_maxrss, 'stop': stop}


def archive_case(task):
    """task = (region_id, mode, nbytes); nbytes < region bytes only for the live preflight."""
    rid, mode, nbytes = task
    meta = json.loads((ASSET / 'structx_assets.json').read_text()); r = meta['regions'][rid]
    raw = (ASSET / r['file']).read_bytes()[:nbytes]
    assert len(raw) == nbytes
    label = f'structx_{rid:02}_mode{mode}_{nbytes}'; work = ROOT / label; work.mkdir()
    (work / 'input.bin').write_bytes(raw); (work / '.dict').symlink_to(ASSET / 'english.dic')
    binary = BIN / f'cmix_structx{mode}'
    env = {k: v for k, v in os.environ.items() if not k.startswith(('LAB_', 'FX_PREPARE', 'HP_LEX_'))}
    env.update(LAB_RAW='1', LAB_DICT=str(ASSET / 'english.dic'), LAB_VOCAB=str(ASSET / 'vocab.bm'), LAB_KEEP_TEMP='1', OMP_NUM_THREADS='1')
    if r['tail'] == 'interlanguage' and mode >= 2:
        env.update(LAB_IW_OWNERS=str(ASSET / r['owners_file']), LAB_IW_BLOCK0=str(r['block0']))
    row = {'mode': mode, 'region': rid, 'tail': r['tail'], 'role': r['role'], 'offset': r['offset'], 'bytes': len(raw),
           'CPU_lane': lanes.LANE_CPU, 'worker_pid': os.getpid(), 'binary_sha256': sha(binary), 'status': 'ENCODING',
           'lab_owner_list': env.get('LAB_IW_OWNERS') is not None}
    record = OUT / (label + '.json'); atomic_json(record, row)
    row['encode'] = run([str(binary), '-n', '--transformer', str(ASSET / 'original.tfwc3'), 'input.bin', 'archive.cmx'], work,
                        {**env, 'LAB_BITTRACE': str(work / 'probabilities.u16')}, 'encode')
    for name in ('encode.log', 'archive.cmx'):
        if (work / name).exists(): shutil.copyfile(work / name, OUT / (label + '_' + name))
    assert row['encode']['exit'] == 0, (label, row['encode'])
    row['status'] = 'INDEPENDENT_DECODE'; atomic_json(record, row)
    row['decode'] = run([str(binary), '-d', '--transformer', str(ASSET / 'original.tfwc3'), 'archive.cmx', 'restored.bin'], work, env, 'decode')
    shutil.copyfile(work / 'decode.log', OUT / (label + '_decode.log'))
    assert row['decode']['exit'] == 0 and (work / 'restored.bin').read_bytes() == raw, (label, 'inverse failed')
    p = work / 'probabilities.u16'; assert p.stat().st_size == 16 * len(raw), 'coded target/trace length differs'
    total = warm = 0.; warmup = r['warmup_bytes'] if nbytes == r['bytes'] else 0
    with p.open('rb') as f:
        for offset in range(0, len(raw), 262144):
            n = min(262144, len(raw) - offset); q = np.frombuffer(f.read(16 * n), dtype='<u2').astype('float64')
            y = np.unpackbits(np.frombuffer(raw[offset:offset + n], dtype='u1')); assert q.min() > 0
            costs = -np.log2(np.where(y, q, 65536 - q) / 65536); total += float(costs.sum())
            begin = max(0, warmup - offset) * 8
            if begin < len(costs): warm += float(costs[begin:].sum())
    with p.open('rb') as f, gzip.open(OUT / (label + '_probabilities.u16.gz'), 'wb', 6) as g: shutil.copyfileobj(f, g)
    row.update(status='COMPLETE_INDEPENDENT_NATIVE_ARCHIVE', archive_bytes=(work / 'archive.cmx').stat().st_size,
               archive_sha256=sha(work / 'archive.cmx'), probabilities_sha256=sha(p), input_sha256=hashlib.sha256(raw).hexdigest(),
               exact_independent_inverse=True, all_target_bits=total, warm_target_bits=warm, warmup_bytes=warmup,
               no_global_history_claim=True, production_build_qualification=False)
    atomic_json(record, row); return row


def main(role, modes, region_ids, nbytes=None, label='v1', asset_dir=None, out_dir=None, root_dir=None, hours=10.3):
    global ASSET, BIN, OUT, ROOT, DEADLINE
    assert role in ('development', 'confirmation', 'preflight') and modes and region_ids
    if asset_dir is None:
        found = list(Path('/kaggle/input').rglob('structx_assets.json')); assert len(found) == 1, found
        ASSET = found[0].parent
    else:
        ASSET = Path(asset_dir)
    ROOT = Path(root_dir or '/root') / ('r14_structx_' + role + '_' + label); ROOT.mkdir()
    OUT = Path(out_dir or '/kaggle/working') / ('structx-' + role + '-' + label); OUT.mkdir()
    DEADLINE = time.monotonic() + hours * 3600
    meta = json.loads((ASSET / 'structx_assets.json').read_text())
    M = {'status': 'VERIFYING_ASSETS', 'started': time.time(), 'role': role, 'modes': list(modes), 'region_ids': list(region_ids),
         'cases': [], 'workers': 4, 'deletions': [], 'GPU': False, 'paid_usd': 0,
         'scope': 'regional PHDA9-tail histories (reset at region start); lab owner list for interlanguage regions; no full-stream or package claim'}
    def save(): atomic_json(OUT / 'manifest.json', M)
    try:
        save()
        for n, rr in meta['files'].items():
            p = ASSET / n; assert p.stat().st_size == rr['bytes'] and sha(p) == rr['sha256'], n
        for rid in region_ids:
            rr = meta['regions'][rid]
            assert role == 'preflight' or rr['role'] == role, (rid, rr['role'], role)
        assert meta['binaries']['cmix_structx0']['sha256'] == '30b539b3ec2cd0a2adf51d3103f2643d113022cce2c7fb17b9828b6f61e10fda'
        # v13 fix: dataset mounts are read-only without execute permission, so binaries are
        # copied to scratch, made executable and re-verified (as every other R14 harness does).
        BIN = ROOT / 'bin'; BIN.mkdir()
        for name, rr in meta['binaries'].items():
            shutil.copyfile(ASSET / name, BIN / name); (BIN / name).chmod(0o700)
            assert sha(BIN / name) == rr['sha256'], name
        M['binary_sha256'] = {name: rr['sha256'] for name, rr in meta['binaries'].items()}
        M['asset_manifest_sha256'] = sha(ASSET / 'structx_assets.json')
        cpus = sorted(os.sched_getaffinity(0))[:4]; assert len(cpus) == 4; M['CPU_lanes'] = cpus
        ctx = mp.get_context('fork'); q = ctx.Queue()
        for c in cpus: q.put(c)
        tasks = []
        for k, rid in enumerate(region_ids):   # rotate mode order by region (counterbalanced queue order)
            ms = list(modes); ms = ms[k % len(ms):] + ms[:k % len(ms)]
            tasks += [(rid, m, nbytes or meta['regions'][rid]['bytes']) for m in ms]
        M['tasks'] = tasks
        before = resource.getrusage(resource.RUSAGE_CHILDREN); M['status'] = 'FOUR_LANE_NATIVE_STRUCTX'; save()
        with ProcessPoolExecutor(4, mp_context=ctx, initializer=initialize_lane, initargs=(q,)) as pool:
            for f in as_completed([pool.submit(archive_case, t) for t in tasks]):
                M['cases'].append(f.result()); save()
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        M.update(status='COMPLETE_NATIVE_STRUCTX_CASES', finished=time.time(),
                 worker_CPU_seconds=after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime)
        M['effective_cores'] = M['worker_CPU_seconds'] / (M['finished'] - M['started']); save()
        return M
    except BaseException as e:
        M.update(status='FAIL_PRESERVED', error=repr(e), traceback=traceback.format_exc(), finished=time.time()); save(); raise
