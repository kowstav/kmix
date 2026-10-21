"""I05 prerequisite: original lex final-bit trace, identity and decode gates.

Restores an isolated source tree, optionally restores clang17 from the official
signed LLVM repository, builds unchanged predictors and validates two cold32K
controls. No native residual predictor is added until these controls PASS.
"""
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import tarfile
import time
import traceback
import urllib.request

import numpy as np
from research_round7_lex_finalbit_trace_patch import exact_lab_changes, patch_texts

OUT = pathlib.Path('/kaggle/working/hp_round7')
DEST = OUT / 'lex_finalbit_trace_v1'
TREE = pathlib.Path('/root/hp/lex_finalbit_trace_v1')
FLAGS = '-DSEED=923 -DUPDATE_LIMIT=3000 -DPPMD_MEM_MB=3500 -DCMIX_L0_LR_SCALE=0.6 -DCMIX_L1_LR_SCALE=0.25 -DCMIX_L0_MIXER_MASK=0x42e72du -DFXCM_CM_DIV=2'
TF = '-DQMAT_CODEBOOK=1 -DQMAT_WMAX=21 -DQMAT_SMALL_W8=1 -DTF_ACTQ_DYN=1 -DTF_AVX512=1'
WEIGHT_SHA = '948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71'
BASE_BINARY_SHA = 'bedd480e36fc3a2ff3bf2150f0eded74f6d4eb4014fb3e35c6be3b5aeeda20c1'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def restore_compiler():
    if not shutil.which('clang++-17'):
        release = pathlib.Path('/etc/os-release').read_text()
        if 'VERSION_CODENAME=jammy' not in release:
            raise RuntimeError('Compiler restore is scoped to Ubuntu Jammy; preserve state and audit another distribution')
        with urllib.request.urlopen('https://apt.llvm.org/llvm-snapshot.gpg.key', timeout=40) as r:
            keydata = r.read()
        key = pathlib.Path('/usr/share/keyrings/hp-round7-llvm17.asc')
        if key.exists() and key.read_bytes() != keydata:
            raise RuntimeError('Existing task key differs; no overwrite')
        if not key.exists():
            key.write_bytes(keydata)
        fpr = subprocess.check_output(['gpg', '--show-keys', '--with-colons', str(key)], text=True)
        assert '6084F3CF814B57C1CF12EFD515CF4D18AF4F7421' in fpr, 'Official LLVM signing fingerprint mismatch'
        repo = pathlib.Path('/etc/apt/sources.list.d/hp-round7-llvm17.list')
        text = 'deb [signed-by=/usr/share/keyrings/hp-round7-llvm17.asc] https://apt.llvm.org/jammy/ llvm-toolchain-jammy-17 main\n'
        if repo.exists() and repo.read_text() != text:
            raise RuntimeError('Existing task repository differs; no overwrite')
        if not repo.exists():
            repo.write_text(text)
        subprocess.run(['apt-get', 'update'], check=True, timeout=450)
        subprocess.run(['apt-get', 'install', '-y', '--no-remove', '--no-install-recommends', 'clang-17', 'lld-17'], check=True, timeout=700)
        (DEST / 'compiler_restore.json').write_text(json.dumps({'source': 'https://apt.llvm.org/',
            'public_key_sha256': hashlib.sha256(keydata).hexdigest(), 'fingerprint': fpr,
            'packages': ['clang-17', 'lld-17'], 'removals_disabled': True,
            'project_deletions': []}, indent=2))
    assert shutil.which('clang++-17') and shutil.which('make'), 'Exact compiler and make required'
    linker = shutil.which('ld.lld-17') or '/usr/lib/llvm-17/bin/ld.lld'
    assert pathlib.Path(linker).is_file(), 'Exact LLVM17 linker required'
    tools = TREE / 'task_bin'
    tools.mkdir()
    (tools / 'ld.lld').symlink_to(linker)
    return str(tools) + os.pathsep + os.environ['PATH']


def extract_sources():
    archive, prefix = OUT / 'preserved/research_sources_and_candidates.tar.gz', 'src/cmix-lex-transformer/'
    TREE.mkdir(parents=True, exist_ok=False)
    with tarfile.open(archive, 'r:gz') as tar:
        selected = [m for m in tar.getmembers() if m.name.startswith(prefix)]
        for m in selected:
            rel = m.name[len(prefix):]
            if not rel:
                continue
            target = (TREE / rel).resolve()
            assert target.is_relative_to(TREE.resolve()), ('Unsafe archive member', m.name)
            if m.issym():
                assert (target.parent / m.linkname).resolve().is_relative_to(TREE.resolve()), ('Unsafe archive symlink', m.name)
            if m.islnk():
                assert m.linkname.startswith(prefix), ('Unsafe archive hardlink', m.name)
            assert m.isfile() or m.isdir() or m.issym() or m.islnk(), ('Unsupported member', m.name)
        for m in selected:
            relative = m.name[len(prefix):]
            if not relative:
                continue
            m.name = relative
            if m.islnk():
                m.linkname = m.linkname[len(prefix):]
            tar.extract(m, TREE, filter='data')
    originals = {n: (TREE / n).read_text() for n in ['src/coder/encoder.cpp', 'src/runner.cpp']}
    patched = patch_texts(originals, exact_lab_changes(OUT / 'research_round7_lex_exact_labpatch.py'))
    for name, text in patched.items():
        (TREE / name).write_text(text)
    makefile = TREE / 'makefile'
    text = makefile.read_text()
    assert '-march=x86-64-v3' in text and '-mrecip=none' in text
    assert '\trm -f *.o\n' in text
    makefile.write_text(text.replace('\trm -f *.o\n', '\t@true\n'))
    return {'archive_sha256': sha(archive),
            'original_instrumented_interfaces_sha256': {n: hashlib.sha256(s.encode()).hexdigest() for n, s in originals.items()},
            'patched_interfaces_sha256': {n: sha(TREE / n) for n in patched},
            'makefile_sha256': sha(makefile)}


def timed(cmd, cwd, env, label):
    begun = time.monotonic()
    log, tf = DEST / (label + '.log'), DEST / (label + '.time')
    with log.open('x') as stream:
        subprocess.run(['/usr/bin/time', '-v', '-o', str(tf), *cmd], cwd=cwd, env=env,
                       stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=500)
    r = {'wall_seconds': time.monotonic() - begun}
    for line in tf.read_text().splitlines():
        if 'User time (seconds)' in line:
            r['user_seconds'] = float(line.rsplit(':', 1)[1])
        if 'System time (seconds)' in line:
            r['system_seconds'] = float(line.rsplit(':', 1)[1])
        if 'Maximum resident set size (kbytes)' in line:
            r['max_rss_kbytes'] = int(line.rsplit(':', 1)[1])
    return r


def main():
    assert not DEST.exists() and not TREE.exists(), 'No duplicate trace build or result overwrite'
    baseline, weights = OUT / 'cmix_round7_lex_codebook', OUT / 'lex_audit/lex_h1_run11.tfwc2'
    assert sha(baseline) == BASE_BINARY_SHA and sha(weights) == WEIGHT_SHA, 'Baseline/model drift'
    assert shutil.disk_usage(OUT).free > 2_000_000_000, 'Preserve space for models and evidence'
    DEST.mkdir()
    result = {'status': 'RUNNING', 'utc_started': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'stage': 'source restoration', 'controls': [], 'neural_training': False, 'paid_rental_usd': 0,
              'deletions': [], 'scope': 'Laboratory identity trace/decode gates; not qualifying package or compression gain'}
    def save(stage):
        result['stage'] = stage
        (DEST / 'results.json').write_text(json.dumps(result, indent=2))
        print(json.dumps({'stage': stage, 'status': result['status']}), flush=True)
    try:
        result['sources'] = extract_sources()
        save('compiler restoration')
        path = restore_compiler()
        env = {**os.environ, 'PATH': path}
        result['compiler'] = subprocess.check_output(['clang++-17', '--version'], text=True).splitlines()[0]
        result['classical_flags'], result['transformer_flags'] = FLAGS, TF
        save('forced native build')
        with (DEST / 'build.log').open('x') as log:
            subprocess.run(['make', '-B', '-j2', 'cmix', 'CC=clang++-17', 'CM_OPT=-O2',
                            'CFLAGS_DEFINES=' + FLAGS, 'CFLAGS_TF_DEFINES=' + TF], cwd=TREE,
                           env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=1800)
        binary = DEST / 'cmix_trace'
        shutil.copy2(TREE / 'cmix', binary)
        result['binary_sha256'], result['binary_bytes'] = sha(binary), binary.stat().st_size
        result['weights_sha256'] = sha(weights)
        save('matched32K identity and independent decode')
        base_env = {k: v for k, v in env.items() if not k.startswith('LAB_')}
        base_env.update(LAB_RAW='1', LAB_VOCAB=str(OUT / 'preserved/data/vocab.bm'),
                        LAB_DICT=str(OUT / 'preserved/gen/.dict'), LAB_KEEP_TEMP='1')
        for n in 'ab':
            raw = (OUT / 'preserved/slices' / (n + '2m.bin')).read_bytes()[:32768]
            inp = DEST / (n + '32k.bin'); inp.write_bytes(raw)
            runs = {}
            for mode, program in [('reference', baseline), ('trace', binary)]:
                d = DEST / (n + '_' + mode); d.mkdir(); (d / '.dict').symlink_to(OUT / 'preserved/gen/.dict')
                e = {**base_env, 'LAB_COST': str(d / 'cost.f32')}
                if mode == 'trace':
                    e['LAB_BITTRACE'] = str(d / 'final_p.u16')
                runs[mode] = timed([str(program), '-n', '--transformer', str(weights), str(inp), 'out.cmx'], d, e, n + '_' + mode)
            a, b = DEST / (n + '_reference'), DEST / (n + '_trace')
            assert (a / 'out.cmx').read_bytes() == (b / 'out.cmx').read_bytes(), ('Native archive identity failed', n)
            ref_cost, trace_cost = np.fromfile(a / 'cost.f32', '<f4'), np.fromfile(b / 'cost.f32', '<f4')
            old_cost = np.fromfile(OUT / 'lex_native_2m' / (n + '_cost.f32'), '<f4')[:len(raw)]
            assert len(ref_cost) == len(trace_cost) == len(raw)
            assert np.array_equal(ref_cost, trace_cost) and np.array_equal(ref_cost, old_cost), ('Native byte-cost drift', n)
            p = np.fromfile(b / 'final_p.u16', '<u2')
            assert len(p) == 8 * len(raw) and np.all((p >= 1) & (p <= 65535)), ('Invalid final-bit trace', n)
            actual = np.unpackbits(np.frombuffer(raw, np.uint8), bitorder='big')
            probability = np.where(actual, p.astype(np.float64), 65536. - p.astype(np.float64)) / 65536.
            reconstructed = (-np.log2(probability)).reshape(-1, 8).sum(axis=1)
            maxdiff = float(np.max(np.abs(reconstructed - ref_cost)))
            assert maxdiff <= 1e-4, ('Final-bit cost reconstruction failed', n, maxdiff)
            decoded = DEST / (n + '_decode'); decoded.mkdir(); (decoded / '.dict').symlink_to(OUT / 'preserved/gen/.dict')
            runs['decode'] = timed([str(binary), '--transformer', str(weights), str(b / 'out.cmx'), 'decoded.bin'], decoded, base_env, n + '_decode')
            assert (decoded / 'decoded.bin').read_bytes() == raw, ('Independent decode failed', n)
            result['controls'].append({'slice': n, 'input_bytes': len(raw), 'input_sha256': sha(inp),
                'archive_bytes': (b / 'out.cmx').stat().st_size, 'archive_sha256': sha(b / 'out.cmx'),
                'bit_trace_sha256': sha(b / 'final_p.u16'), 'bit_count': len(p),
                'max_bit_reconstruction_vs_float32_byte_cost_diff': maxdiff,
                'archive_bit_exact_reference': True, 'costs_bit_exact_older2M_prefix': True,
                'independent_raw_decode_exact': True, 'runtime': runs})
            save('matched32K controls ' + n + ' PASS')
        result['status'] = 'PASS'
        save('all identity trace/decode gates passed; residual screen pending')
        print('LEX_FINALBIT_TRACE_GATES_COMPLETE', flush=True)
    except Exception:
        result['status'], result['error'] = 'FAIL', traceback.format_exc()
        save('failed; source/models/logs preserved; no automatic relaunch')
        raise


if __name__ == '__main__':
    main()
