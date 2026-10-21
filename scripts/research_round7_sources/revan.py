# Analyse PHDA9 revision records in the tail: fields, and how predictable revision ids are from
# timestamps given the previously coded records (decoder-side, causal).
import re, math, bisect, collections, numpy as np
data = open('/root/hp/gen/.main_phda9prepr', 'rb').read()
i = data.rfind(b'</page>') + 8
tail = data[i:]
lines = tail.split(b'\n')
recs = []
j = 0
while j < len(lines) and not lines[j].startswith(b'revision>'): j += 1
first = j
kinds = collections.Counter()
while j < len(lines):
    if not lines[j].startswith(b'revision>'):
        break
    r = {'extra': [], 'other': []}
    j += 1
    while j < len(lines) and not lines[j].startswith(b'revision>'):
        L = lines[j]
        if L.startswith(b'[') or L.startswith(b'{') or b'</text' in L: break
        if L.startswith(b'id>') and 'revid' not in r: r['revid'] = int(L[3:])
        elif L.startswith(b'timestamp>'): r['ts'] = L[10:].decode()
        elif L.startswith(b'username>'): r['user'] = L[9:]
        elif L.startswith(b'id>'): r['uid'] = int(L[3:])
        elif L.startswith(b'ip>'): r['ip'] = L[3:]
        elif L in (b'contributor>', b'/contributor>'): pass
        elif L.startswith(b'>'): r['extra'].append(L)
        else: r['other'].append(L); kinds[L.split(b'>')[0]] += 1
        j += 1
    recs.append(r)
    if j < len(lines) and not lines[j].startswith(b'revision>'): break
print('records', len(recs), 'stopped at line', j, 'of', len(lines), repr(lines[j][:80]) if j < len(lines) else '')
print('other field kinds', kinds.most_common(10))
rec_bytes = sum(len(l) + 1 for l in lines[first:j])
print('record region bytes', rec_bytes, 'remaining tail bytes', len(tail) - rec_bytes)
ex = collections.Counter(len(r['extra']) for r in recs)
print('extra-line counts', ex.most_common(5))
recs = [r for r in recs if 'revid' in r and 'ts' in r]
# timestamp format day:sec ; parse
def ts2s(t):
    d, s = t.split(':'); return int(d) * 86400 + int(s)
T = np.array([ts2s(r['ts']) for r in recs], dtype=np.int64)
R = np.array([r['revid'] for r in recs], dtype=np.int64)
print('ts range', T.min(), T.max(), 'revid range', R.min(), R.max())
# monotonicity check: correlation of rank
ordT = np.argsort(T, kind='stable'); inv = R[ordT]
print('fraction of adjacent (by time) pairs with increasing revid:', np.mean(np.diff(inv) > 0))
# causal predictor: for record k, predict revid from timestamp using previously seen records:
# find neighbours in time among seen records (sorted list), linear interpolation.
seenT = []; seenR = []
res = []
for k in range(len(recs)):
    t, r = int(T[k]), int(R[k])
    if len(seenT) >= 2:
        p = bisect.bisect_left(seenT, t)
        lo = max(0, p - 1); hi = min(len(seenT) - 1, p)
        if lo == hi:
            if hi == 0: lo, hi = 0, 1
            else: lo, hi = hi - 1, hi
        t0, t1, r0, r1 = seenT[lo], seenT[hi], seenR[lo], seenR[hi]
        pred = r0 if t1 == t0 else r0 + (r1 - r0) * (t - t0) / (t1 - t0)
        res.append(r - pred)
    p = bisect.bisect_left(seenT, t)
    seenT.insert(p, t); seenR.insert(p, r)
res = np.array(res)
a = np.abs(res)
for q in [50, 75, 90, 95, 99]:
    print(f'|revid residual| p{q} = {np.percentile(a, q):.0f}')
# entropy estimate of residual with Elias-gamma-like / log2 cost
est = np.mean(np.log2(a + 1) * 1.0 + 2.0)
print('approx bits per revid with interpolation coding ~', est, ' vs raw digits ~', np.mean(np.log2(R)))
# timestamp predictability from revid (reverse)
users = collections.Counter(r.get('user') for r in recs if 'user' in r)
print('distinct users', len(users), 'records with user', sum(users.values()), 'ip records', sum(1 for r in recs if 'ip' in r))
# uid determinism: is uid a function of user?
m = {}; bad = 0
for r in recs:
    if 'user' in r:
        if r['user'] in m and m[r['user']] != r['uid']: bad += 1
        m[r['user']] = r['uid']
print('user->uid violations', bad)
first_seen = sum(1 for u in users)  # each user's first appearance needs its uid coded
print('records whose user was seen before (uid predictable):', sum(users.values()) - len(users))
