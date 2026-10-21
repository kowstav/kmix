# Interwiki title-copy transform (experiment): in each interlanguage block, replace a link title
# that equals the owning article's English title by the marker byte 0x01. Decoder-side inverse
# uses the titles of articles lacking '</text>' in the main stream (block k <-> k-th such article).
# usage: python iwtx.py NBLOCKS out_prefix
import sys, re
N = int(sys.argv[1]); OUT = sys.argv[2]
d = open('/root/hp/gen/.main_phda9prepr', 'rb').read()
i = d.rfind(b'</page>') + 8
main, tail = d[:i], d[i:]
pages = main.split(b'<page>')[1:]
titles = []
for p in pages:
    if b'</text>' not in p:
        m = re.search(rb'<title>([^<\n]*)</title>', p)
        titles.append(m.group(1) if m else b'')
s = tail.find(b'[', tail.rfind(b'/contributor>'))
iw = tail[s:]
blocks = iw.split(b'</text>\n')
n = min(N, len(blocks) - 1)
ent_re = re.compile(rb'^\[([a-z\-]+):(.*)\]$')
orig_parts, tx_parts = [], []
ncopy = nent = 0
for k in range(n):
    title = titles[k]
    out = []
    for ln in blocks[k].split(b'\n'):
        m = ent_re.match(ln)
        if m:
            nent += 1
            if m.group(2) == title:
                ncopy += 1
                ln = b'[' + m.group(1) + b':\x01]'
        out.append(ln)
    orig_parts.append(blocks[k] + b'</text>\n')
    tx_parts.append(b'\n'.join(out) + b'</text>\n')
orig = b''.join(orig_parts); tx = b''.join(tx_parts)
# verify inverse
inv = []
for k, blk in enumerate(tx.split(b'</text>\n')[:-1]):
    inv.append(blk.replace(b':\x01]', b':' + titles[k] + b']') + b'</text>\n')
assert b''.join(inv) == orig
open(OUT + '.orig.txt', 'wb').write(orig); open(OUT + '.tx.txt', 'wb').write(tx)
print('blocks', n, 'entries', nent, 'title copies', ncopy, 'orig bytes', len(orig), 'tx bytes', len(tx))
