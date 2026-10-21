"""Repair the short-file vocabulary mismatch without modifying native bytes."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
import traceback

W = Path('/kaggle/working')
D = W / 'hp_round11/preflight_v4'
D.mkdir(parents=True, exist_ok=False)
S = Path('/root/hp_round11/preflight_v4')
S.mkdir(parents=True, exist_ok=False)
T = W / 'hp_round8/native_stage_trace_v1/tree'
B = T / 'cmix'
B.chmod(B.stat().st_mode | 0o100)
N = 16384
M = {'status': 'RUNNING', 'pid': os.getpid(), 'started': time.time(), 'cases': [],
     'scratch': str(S), 'input_bytes': N, 'deletions': [], 'paid_usd': 0,
     'repair': 'Forced vocabulary must be serialized: original header omits the bitmap for length <10000; corrected preflight uses 16384 bytes.',
     'prior_failed_job': '/kaggle/working/hp_round10/preflight_v3/manifest.json'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save():
    (D / 'manifest.json').write_text(json.dumps(M, indent=2))

try:
    assert sha(B) == '17768b0673e5a1ad6fb39ca86af25d6d40db3b1790fc17e365341456819fd3fa'
    with (W / 'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt').open('rb') as f:
        raw = f.read(N)
    assert len(raw) == N and N >= 10000
    (S / 'input.bin').write_bytes(raw)
    (S / '.dict').symlink_to(T / 'dictionary/english.dic')
    weights = W / 'hp_round7/lex_audit/lex_h1_run11.tfwc2'
    vocab = W / 'hp_round7/preserved/data/vocab.bm'
    env = {k:v for k,v in os.environ.items() if not k.startswith(('LAB_', 'FX_PREPARE', 'HP_LEX_'))}
    env.update(LAB_RAW='1', LAB_DICT=str(T/'dictionary/english.dic'), LAB_VOCAB=str(vocab), LAB_KEEP_TEMP='1', OMP_NUM_THREADS='1')
    save()
    for label, args in [('encode', [str(B), '-n', '--transformer', str(weights), 'input.bin', 'out.cmx']),
                        ('decode', [str(B), '-d', '--transformer', str(weights), 'out.cmx', 'decoded.bin'])]:
        started = time.monotonic()
        with (D / (label+'.log')).open('x') as log:
            p = subprocess.Popen(args, cwd=S, env=env, stdout=log, stderr=subprocess.STDOUT)
            M['child_pid'] = p.pid
            M['stage'] = label
            save()
            _, status, usage = os.wait4(p.pid, 0)
        code = os.waitstatus_to_exitcode(status)
        M['cases'].append({'name':label, 'exit_code':code, 'wall_seconds':time.monotonic()-started,
                           'CPU_user_seconds':usage.ru_utime, 'CPU_system_seconds':usage.ru_stime, 'peak_RSS_KiB':usage.ru_maxrss})
        save()
        assert code == 0, (label, code)
        if label == 'encode':
            header = (S/'out.cmx').read_bytes()[:37]
            assert (int.from_bytes(header[:5], 'big') & ((1<<39)-1)) == N
            assert header[5:37] == vocab.read_bytes()
            M['serialized_vocabulary_exact'] = True
    assert (S/'decoded.bin').read_bytes() == raw
    M.update(status='COMPLETE_NATIVE_PREFLIGHT_PASS_SERIALIZED_VOCABULARY', input_sha256=sha(S/'input.bin'),
             archive_sha256=sha(S/'out.cmx'), archive_bytes=(S/'out.cmx').stat().st_size, independent_decode_exact=True, finished=time.time())
    save()
except BaseException as error:
    M.update(status='FAIL', error=repr(error), traceback=traceback.format_exc(), finished=time.time())
    save()
    raise
