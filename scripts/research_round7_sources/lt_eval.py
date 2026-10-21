# lt_eval: link-target expert screening against the FINAL coder (per-byte cost dump).
# Inside an internal link (post-WRT '[' ... ']' / '|' / '#'), predict the next byte from the set of strings
# decoded earlier: article titles (WRT form) and earlier link targets (weighted by count).
# Byte-level online Bayesian mixture (alpha grid, per context) of coder prob and expert prob of the actual byte.
import sys, re, math, bisect, mmap
import numpy as np
from collections import defaultdict

ST = '/root/hp/data/stream.bin'
REC_ABS = 554867470
SEP = b'  L\xdf\x98N\n    L\xdf\x9bN'
TEND = b'L/\xdf\x9bN'
slice_path, cost_path = sys.argv[1], sys.argv[2]
sl = open(slice_path, 'rb').read()
cost = np.fromfile(cost_path, dtype=np.float32).astype(np.float64)
assert len(cost) == len(sl)
f = open(ST, 'rb'); m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
off = m.find(sl[:200])
assert off >= 0 and m[off:off + len(sl)] == sl
print('slice offset', off)

W = defaultdict(float)   # string -> weight
def add_titles_links(buf):
    for t in re.finditer(re.escape(SEP) + rb'(.*?)' + re.escape(TEND), buf):
        W[t.group(1)] += 1.0
    for t in re.finditer(rb'\[([^\[\]\|#\n]{1,120})[\]\|#]', buf):
        W[t.group(1)] += 1.0
add_titles_links(m[:off])
keys = sorted(W)
print('prior strings', len(keys))

def expert(prefix):
    lo = bisect.bisect_left(keys, prefix)
    hi = bisect.bisect_left(keys, prefix + b'\xff\xff\xff\xff')
    if hi - lo == 0 or hi - lo > 4000:
        return None, hi - lo
    d = defaultdict(float); L = len(prefix)
    for s in keys[lo:hi]:
        w = W[s]
        if len(s) == L:
            d[256] += w            # string ends here: next byte is a terminator
        else:
            d[s[L]] += w
    return d, hi - lo

grid = np.linspace(0, 1, 11)
post = defaultdict(lambda: np.zeros(11))
eps = 0.02
tot_c = 0.0; tot_m = 0.0; nact = 0; link_bits = 0.0; link_bytes = 0
i = 0; inlink = False; pre = b''
by = defaultdict(lambda: [0, 0.0, 0.0])
newstr = []
tstart = -1
n = len(sl)
while i < n:
    c = sl[i]
    if inlink:
        link_bytes += 1; link_bits += cost[i]
        d, cnt = expert(pre)
        if d is not None:
            Z = sum(d.values())
            if c in (0x5D, 0x7C, 0x23):
                pe = d.get(256, 0.0) / Z
                # split terminator mass over the three terminators by fixed shares
                pe *= {0x5D: 0.8, 0x7C: 0.18, 0x23: 0.02}[c]
            else:
                pe = d.get(c, 0.0) / Z
            pe = (1 - eps) * pe + eps / 205.0
            pc = 2.0 ** (-cost[i])
            ctx = (min(len(pre), 6), min(int(math.log2(cnt)) if cnt else 0, 12))
            lp = post[ctx]; w = np.exp(lp - lp.max()); w /= w.sum()
            pm = float((w * ((1 - grid) * pc + grid * pe)).sum())
            post[ctx] = lp + np.log((1 - grid) * pc + grid * pe)
            tot_c += cost[i]; tot_m += -math.log2(pm); nact += 1
            r = by[ctx[1]]; r[0] += 1; r[1] += cost[i]; r[2] += -math.log2(pm)
        if c in (0x5D, 0x7C, 0x23, 0x0A, 0x5B):
            inlink = False
            if c != 0x0A and c != 0x5B and pre:
                newstr.append(pre)
        else:
            pre += bytes([c])
    elif c == 0x5B:   # '['
        inlink = True; pre = b''
    if sl.startswith(SEP, i):
        tstart = i + len(SEP)
    if tstart >= 0 and sl.startswith(TEND, i):
        newstr.append(sl[tstart:i]); tstart = -1
    # insert completed strings once an article boundary passes (keeps lookups cheap and causal)
    if sl.startswith(SEP, i) and newstr:
        for s in newstr:
            if s not in W:
                bisect.insort(keys, s)
            W[s] += 1.0
        newstr = []
    i += 1
print('slice bytes %d, total coder %.0f B; link-target bytes %d cost %.0f B' % (n, cost.sum() / 8, link_bytes, link_bits / 8))
print('expert-active bytes %d: coder %.0f B -> mixed %.0f B (delta %.0f B, %.3f%% of slice)' % (
    nact, tot_c / 8, tot_m / 8, (tot_m - tot_c) / 8, 100 * (tot_m - tot_c) / cost.sum()))
for k in sorted(by):
    r = by[k]; print('  log2(cands)=%2d  n=%7d  coder %.3f  mixed %.3f bits/byte' % (k, r[0], r[1] / r[0], r[2] / r[0]))
