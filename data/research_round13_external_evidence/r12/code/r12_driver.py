"""R12 driver: one native encode of a canonical slice + streaming replay of all arms.

The native binary and model are unchanged (replay only).  Traces are regular files
followed by the consumer, which punches holes behind its read position.
"""
import gzip, hashlib, json, os, shutil, signal, subprocess, time
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while b := f.read(1 << 22):
            h.update(b)
    return h.hexdigest()


def compile_consumer(code_dir, exe):
    r = subprocess.run(['g++', '-O2', '-std=c++17', '-fno-fast-math', '-ffp-contract=off', '-I', str(code_dir),
                        str(Path(code_dir) / 'stream_replay.cpp'), '-o', str(exe)], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('consumer compile failed: ' + r.stderr[-2000:])
    return {'compiler': subprocess.run(['g++', '--version'], capture_output=True, text=True).stdout.splitlines()[0],
            'flags': '-O2 -std=c++17 -fno-fast-math -ffp-contract=off', 'exe_sha256': sha(exe)}


def run_case(*, label, slice_bytes, abs_offset, binary, weights, dictionary, vocab, consumer, work, out_dir,
             budget_seconds, cpu_encoder=0, cpu_consumer=1, punch=True, window=524288, min_free_gb=6.0,
             keep_cost=True, manifest=None, save=None):
    work = Path(work); out_dir = Path(out_dir)
    work.mkdir(parents=True, exist_ok=False); out_dir.mkdir(parents=True, exist_ok=True)
    (work / 'input.bin').write_bytes(slice_bytes)
    (work / '.dict').symlink_to(dictionary)
    rec = {'label': label, 'abs_offset': abs_offset, 'bytes_requested': len(slice_bytes),
           'input_sha256': hashlib.sha256(slice_bytes).hexdigest(), 'window_bytes': window,
           'cpu_encoder': cpu_encoder, 'cpu_consumer': cpu_consumer, 'status': 'RUNNING'}
    if manifest is not None:
        manifest.setdefault('cases', []).append(rec)
    def persist(stage):
        rec['stage'] = stage
        if save: save()
    paths = {k: work / k for k in ['final_p.u16', 'stage.f32', 'hidden.q8', 'cost.f32']}
    done = work / 'encoder.done'
    out_jsonl = out_dir / f'{label}.jsonl'
    env = {k: v for k, v in os.environ.items() if not k.startswith(('LAB_', 'FX_PREPARE', 'HP_LEX_'))}
    env.update(LAB_RAW='1', LAB_VOCAB=str(vocab), LAB_DICT=str(dictionary), LAB_KEEP_TEMP='1', OMP_NUM_THREADS='1',
               LAB_COST=str(paths['cost.f32']), LAB_BITTRACE=str(paths['final_p.u16']),
               LAB_STAGETRACE=str(paths['stage.f32']), LAB_HIDDENTRACE=str(paths['hidden.q8']))
    cons = subprocess.Popen([str(consumer), str(work / 'input.bin'), str(paths['final_p.u16']), str(paths['stage.f32']),
                             str(paths['hidden.q8']), str(done), str(out_jsonl), str(window), str(abs_offset),
                             '1' if punch else '0'], cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            preexec_fn=lambda: os.sched_setaffinity(0, {cpu_consumer}))
    started = time.monotonic()
    enc = subprocess.Popen([str(binary), '-n', '--transformer', str(weights), 'input.bin', 'out.cmx'], cwd=work, env=env,
                           stdout=open(work / 'encode.log', 'wb'), stderr=subprocess.STDOUT,
                           preexec_fn=lambda: os.sched_setaffinity(0, {cpu_encoder}))
    rec['encoder_pid'] = enc.pid; rec['consumer_pid'] = cons.pid
    persist('encode running')
    stop_reason = None
    while True:
        try:
            pid, status, usage = os.wait4(enc.pid, os.WNOHANG)
        except ChildProcessError:
            pid = enc.pid; status = 0; usage = None
        if pid == enc.pid:
            break
        elapsed = time.monotonic() - started
        free_gb = shutil.disk_usage(work).free / 1e9
        progressed = paths['cost.f32'].stat().st_size // 4 if paths['cost.f32'].exists() else 0
        rec['progress'] = {'elapsed_s': round(elapsed), 'bytes_encoded_approx': progressed, 'free_gb': round(free_gb, 1)}
        if stop_reason is None and (elapsed > budget_seconds or free_gb < min_free_gb):
            stop_reason = 'time budget' if elapsed > budget_seconds else 'disk guard'
            rec['stopped_early'] = stop_reason
            enc.send_signal(signal.SIGTERM)
        if cons.poll() is not None and cons.returncode != 0:
            enc.send_signal(signal.SIGTERM); stop_reason = stop_reason or 'consumer failed'
        persist('encode running')
        time.sleep(30)
    code = os.waitstatus_to_exitcode(status) if usage else None
    rec['encode'] = {'wall_seconds': time.monotonic() - started, 'exit_code': code,
                     'CPU_user_seconds': usage.ru_utime if usage else None,
                     'CPU_system_seconds': usage.ru_stime if usage else None,
                     'peak_RSS_KiB': usage.ru_maxrss if usage else None}
    done.write_text('done')
    persist('waiting for consumer')
    try:
        out, _ = cons.communicate(timeout=3600)
    except subprocess.TimeoutExpired:
        cons.kill(); out, _ = cons.communicate()
    rec['consumer_exit'] = cons.returncode
    rec['consumer_output'] = out.decode(errors='replace')[-2000:]
    rows = [json.loads(l) for l in out_jsonl.read_text().splitlines() if l.strip()] if out_jsonl.exists() else []
    summary = next((r for r in rows if r.get('type') == 'summary'), None)
    errors = [r for r in rows if r.get('type') == 'error']
    rec['summary'] = summary; rec['errors'] = errors
    # Cross-check the replay baseline against the native per-byte cost file (same native p).
    if summary and paths['cost.f32'].exists():
        import numpy as np
        nbytes = summary['bytes']
        cost = np.fromfile(paths['cost.f32'], dtype='<f4', count=nbytes).astype(np.float64)
        rec['cost_trace_bits_processed_bytes'] = float(cost.sum())
        rec['baseline_minus_cost_bits'] = float(summary['baseline_bits'] - cost.sum())
        if keep_cost:
            with open(paths['cost.f32'], 'rb') as src, gzip.open(out_dir / f'{label}_cost.f32.gz', 'wb', 6) as dst:
                shutil.copyfileobj(src, dst)
    if code == 0 and (work / 'out.cmx').exists():
        rec['archive_bytes'] = (work / 'out.cmx').stat().st_size
        rec['archive_sha256'] = sha(work / 'out.cmx')
    ok = summary is not None and not errors and summary['identity_mismatch_bits'] == 0 and cons.returncode == 0
    rec['status'] = ('COMPLETE' if code == 0 else 'TRUNCATED_' + (stop_reason or 'encoder_exit')) if ok else 'FAIL'
    persist('case finished')
    return rec
