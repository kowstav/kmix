"""User-run cleanup of hash-verified, non-essential files on /kaggle/working.

Prepared by the Claude audit (round 12).  It removes a file ONLY if its current
SHA-256 still equals the value recorded in cleanup_candidates.json and, for a
duplicate, its twin still exists with the identical hash.  Every action is
appended to cleanup_ledger.json.  Run:  python3 cleanup_verified.py --apply
Without --apply it only reports what it would remove.
"""
import hashlib, json, os, sys, time
from pathlib import Path
HERE = Path('/kaggle/working/hp_round12_claude')
apply = '--apply' in sys.argv
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while b := f.read(1 << 22): h.update(b)
    return h.hexdigest()
cands = json.loads((HERE / 'cleanup_candidates.json').read_text())
ledger = {'run': time.time(), 'apply': apply, 'actions': []}
freed = 0
for c in cands:
    p = Path(c['path']); act = {'path': str(p), 'bytes': c['bytes']}
    if not p.exists():
        act['result'] = 'absent'; ledger['actions'].append(act); continue
    h = sha(p)
    if h != c['sha256']:
        act['result'] = 'SKIPPED_HASH_CHANGED'; ledger['actions'].append(act); continue
    if c.get('verified_identical'):
        twin = Path(c['reason'].split('duplicate of ', 1)[1])
        if not twin.exists() or sha(twin) != h:
            act['result'] = 'SKIPPED_TWIN_MISSING_OR_DIFFERENT'; ledger['actions'].append(act); continue
    if apply:
        p.unlink(); act['result'] = 'REMOVED'; freed += c['bytes']
    else:
        act['result'] = 'WOULD_REMOVE'
    ledger['actions'].append(act)
ledger['freed_bytes'] = freed
(HERE / 'cleanup_ledger.json').write_text(json.dumps(ledger, indent=1))
for a in ledger['actions']: print(f"{a['result']:34s} {a['bytes']/1e6:9.1f} MB  {a['path']}")
print('freed GB', round(freed / 1e9, 3), '(dry run)' if not apply else '')
