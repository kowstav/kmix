# Reversible "revid from timestamp" transform of PHDA9 revision records (experiment).
# forward: in each record put the timestamp line first and replace the revision id by
#   its residual against a causal integer interpolation over previously coded records.
# inverse: exact reconstruction. Also writes the untouched region for A/B.
# usage: python revtx.py NREC out_prefix
import sys, bisect
NREC = int(sys.argv[1]); OUT = sys.argv[2]
data = open('/root/hp/gen/.main_phda9prepr', 'rb').read()
i = data.rfind(b'</page>') + 8
tail = data[i:]
lines = tail.split(b'\n')
j = 0
while not lines[j].startswith(b'revision>'): j += 1
start = j
recs = []  # list of line lists
while j < len(lines) and len(recs) < NREC and lines[j].startswith(b'revision>'):
    k = j + 1
    while k < len(lines) and not lines[k].startswith(b'revision>') and not lines[k].startswith(b'['):
        k += 1
    recs.append(lines[j:k]); j = k
orig = b'\n'.join(lines[start:j]) + b'\n'

def ts2s(t):
    d, s = t.split(b':'); return int(d) * 86400 + int(s)

class Pred:
    def __init__(self): self.T = []; self.R = []
    def predict(self, t):
        T, R = self.T, self.R
        if not T: return 30000000
        if len(T) == 1: return R[0]
        p = bisect.bisect_left(T, t)
        lo, hi = max(0, p - 1), min(len(T) - 1, p)
        if lo == hi: lo, hi = (0, 1) if hi == 0 else (hi - 1, hi)
        t0, t1, r0, r1 = T[lo], T[hi], R[lo], R[hi]
        if t1 == t0: return r0
        return r0 + ((r1 - r0) * (t - t0)) // (t1 - t0)   # exact integer arithmetic
    def add(self, t, r):
        p = bisect.bisect_left(self.T, t); self.T.insert(p, t); self.R.insert(p, r)

def forward(recs):
    P = Pred(); out = []
    for rec in recs:
        assert rec[0] == b'revision>' and rec[1].startswith(b'id>') and rec[2].startswith(b'timestamp>'), rec[:3]
        r = int(rec[1][3:]); tline = rec[2]; t = ts2s(tline[10:])
        res = r - P.predict(t); P.add(t, r)
        out.append(b'\n'.join([rec[0], tline, b'id>%d' % res] + rec[3:]))
    return b'\n'.join(out) + b'\n'

def inverse(txt):
    P = Pred(); out = []
    L = txt.split(b'\n')[:-1]
    k = 0
    while k < len(L):
        assert L[k] == b'revision>'
        m = k + 1
        while m < len(L) and L[m] != b'revision>': m += 1
        rec = L[k:m]; tline = rec[1]; t = ts2s(tline[10:])
        r = P.predict(t) + int(rec[2][3:]); P.add(t, r)
        out.append(b'\n'.join([rec[0], b'id>%d' % r, tline] + rec[3:])); k = m
    return b'\n'.join(out) + b'\n'

tx = forward(recs)
assert inverse(tx) == orig, 'inverse mismatch'
open(OUT + '.orig.txt', 'wb').write(orig)
open(OUT + '.tx.txt', 'wb').write(tx)
print('records', len(recs), 'orig bytes', len(orig), 'tx bytes', len(tx), 'inverse verified')
