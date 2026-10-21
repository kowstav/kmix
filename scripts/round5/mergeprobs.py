# Build an adapted probs file for slice [A,B): start from the baseline slice probs file
# (PPMD rows at piece ends, transformer rows elsewhere) and overwrite transformer rows with
# the adapted distributions written by headadapt (dump prefix .row gives predicted-token index).
# usage: python mergeprobs.py dumpprefix adapted.f16 base_slice_prefix A B out.probs.f16
import sys, numpy as np
dp, adf, base, A, B, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
V = 205
rows = np.fromfile(dp + '.row', dtype=np.int64)          # predicted token index of each position
ad = np.memmap(adf, dtype=np.float16, mode='r').reshape(-1, V)
assert len(ad) == len(rows)
P = np.fromfile(base + '.probs.f16', dtype=np.float16).reshape(-1, V).copy()
assert len(P) == B - A
k = rows - 1                                               # file row index (predicts token k+1)
sel = (k >= A) & (k < B)
P[k[sel] - A] = ad[sel]
P.tofile(out)
print('replaced', int(sel.sum()), 'of', B - A, 'rows')
