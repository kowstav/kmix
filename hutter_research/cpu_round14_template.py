"""P5 paid constructor-run templates: four-lane development screen / confirmation job.

Regions are exactly cpu_round14_constructor.offsets() (32 spread 1 MiB original-text
regions, seed 1400831; even index = development, odd = confirmation), the same regions as
the 608 completed constructor archives. Static template tables are built from
development regions only: leave-one-out for the development screen (region i never sees
its own runs), and all sixteen development regions for confirmation. Every table is paid
inside every archive. Every case independently decodes to its exact input. Arms with no
dictionary must reproduce constructor_codec's coarse_<ctx>:4 sequence stream byte for byte.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import gzip, hashlib, json, multiprocessing as mp, os, resource, time, traceback
from .cpu_round13_jobs import atomic_json, initialize_lane, sha
from . import cpu_round13_jobs as lanes
from . import template_codec as T
from . import constructor_codec as C
from .cpu_round14_constructor import offsets

ROOT = OUT = None
TABLES = None   # role-specific: {(region_index, cap): [templates]}
DEV_GRID = ([('left', 'none', 0, 0), ('right', 'none', 0, 0), ('wrong', 'none', 0, 0)] +
            [(c, k, cap, e) for k in ('static', 'prefix') for cap in (64, 256) for e in (0, 1, 2) for c in ('left', 'right', 'wrong')])


def region_bytes(i):
    with (ROOT / 'original_enwik9.bin').open('rb') as f:
        f.seek(offsets()[i]); return f.read(1048576)


def case(task):
    i, (ctx, kind, cap, E) = task
    raw = region_bytes(i); start = time.monotonic(); u = resource.getrusage(resource.RUSAGE_SELF)
    templates = TABLES[(i, cap)] if kind == 'static' else None
    st = {}; blob = T.encode(raw, ctx, kind, cap, E, templates, stats=st); assert T.decode(blob) == raw
    a = resource.getrusage(resource.RUSAGE_SELF)
    label = f'template_{i:02}_{ctx}_{kind}_{cap}_{E}'; (OUT / (label + '.hptpl')).write_bytes(blob)
    row = {'index': i, 'offset': offsets()[i], 'role': 'development' if i % 2 == 0 else 'confirmation',
           'ctx': ctx, 'kind': kind, 'cap': cap, 'edit_cap': E, 'input_bytes': len(raw),
           'input_sha256': hashlib.sha256(raw).hexdigest(), 'archive_bytes': len(blob),
           'archive_sha256': hashlib.sha256(blob).hexdigest(), 'channels': T.inspect_sizes(blob), 'stats': st,
           'template_table_sha256': hashlib.sha256(T.serialize_table(templates)).hexdigest() if templates is not None else None,
           'templates_in_table': len(templates) if templates is not None else 0,
           'exact_inverse': True, 'CPU_lane': lanes.LANE_CPU, 'CPU_seconds': a.ru_utime + a.ru_stime - u.ru_utime - u.ru_stime,
           'wall_seconds': time.monotonic() - start, 'peak_RSS_KiB': a.ru_maxrss}
    if kind == 'none':
        old = C.encode(raw, T.CTX[ctx], T.ALPHA); osz = C.inspect_sizes(old)
        o0 = 50 + sum(list(osz.values())[:5]); n0 = T.HSIZE + sum(list(row['channels'].values())[:5])
        same = old[o0:o0 + osz['constructor_sequence']] == blob[n0:n0 + row['channels']['run_stream']]
        assert same and len(blob) == len(old) + (T.HSIZE - 50), 'baseline identity with constructor_codec failed'
        row['constructor_codec_identity'] = {'old_archive_bytes': len(old), 'old_sha256': hashlib.sha256(old).hexdigest(),
                                             'sequence_stream_identical': True, 'header_delta_bytes': T.HSIZE - 50}
        if ctx == 'right':
            import zstandard as zstd
            row['gzip_bytes'] = len(gzip.compress(raw, mtime=0)); row['zstd_bytes'] = len(zstd.ZstdCompressor(level=9).compress(raw))
    atomic_json(OUT / (label + '.json'), row); return row


def build_tables(role, indices_dev, caps=(64, 256)):
    runs = {i: T.constructor_runs(region_bytes(i)) for i in indices_dev}
    tables, meta = {}, {}
    targets = indices_dev if role == 'development' else [i for i in range(32) if i % 2 == 1]
    for i in targets:
        trie = T.RunTrie()
        for j in indices_dev:
            if role == 'development' and j == i: continue   # leave-one-out
            for r in runs[j]: trie.insert(r)
        for cap in caps:
            t = T.select_templates(trie, cap); tables[(i, cap)] = t
            meta[f'{i}:{cap}'] = {'templates': len(t), 'sha256': hashlib.sha256(T.serialize_table(t)).hexdigest(),
                                   'source_regions': [j for j in indices_dev if not (role == 'development' and j == i)]}
    return tables, meta


def main(role, grid=None, label='v1'):
    global ROOT, OUT, TABLES
    assert role in ('development', 'confirmation')
    grid = [tuple(g) for g in (grid or DEV_GRID)]
    from . import cpu_round13_jobs as old
    paths = list(Path('/kaggle/input').rglob('r13_assets.json')); assert len(paths) == 1
    ROOT = Path('/root/r14_template_' + role + '_' + label); ROOT.mkdir()
    OUT = Path('/kaggle/working/template-' + role + '-' + label); OUT.mkdir()
    old.ROOT = ROOT; old.ASSET = paths[0].parent; source = old.raw_source()
    M = {'status': 'PREFLIGHT', 'started': time.time(), 'role': role, 'grid': grid, 'cases': [], 'workers': 4,
         'offsets': offsets(), 'raw_source_sha256': sha(source), 'deletions': [], 'GPU': False, 'paid_usd': 0,
         'limits': 'paid raw-text proxy; not the native stream; tables paid per archive'}
    def save(): atomic_json(OUT / 'manifest.json', M)
    try:
        save(); cpus = sorted(os.sched_getaffinity(0))[:4]; assert len(cpus) == 4
        probe = b'There was a camel. The the AND it.\x00\xff of the of the in the'
        for ctx, kind, cap, E in grid:
            assert T.decode(T.encode(probe, ctx, kind, cap, E, [(1, 2), (3, 4, 5)] if kind == 'static' else None)) == probe
        dev = [i for i in range(32) if i % 2 == 0]
        TABLES, M['tables'] = build_tables(role, dev); save()
        ctxm = mp.get_context('fork'); q = ctxm.Queue()
        for c in cpus: q.put(c)
        targets = dev if role == 'development' else [i for i in range(32) if i % 2 == 1]
        tasks = [(i, g) for i in targets for g in grid]
        before = resource.getrusage(resource.RUSAGE_CHILDREN); M.update(status='FOUR_LANE_RUNNING', case_count=len(tasks)); save()
        with ProcessPoolExecutor(4, mp_context=ctxm, initializer=initialize_lane, initargs=(q,)) as pool:
            for f in as_completed([pool.submit(case, t) for t in tasks]): M['cases'].append(f.result()); save()
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        M.update(status='COMPLETE_ALL_PAID_TEMPLATE_INVERSES', finished=time.time(),
                 worker_CPU_seconds=after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime)
        M['effective_cores'] = M['worker_CPU_seconds'] / (M['finished'] - M['started']); save()
    except BaseException as e:
        M.update(status='FAIL_PRESERVED', error=repr(e), traceback=traceback.format_exc(), finished=time.time()); save(); raise
