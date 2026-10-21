# Interwiki statistics on original enwik9: how often does an interlanguage link title
# equal (or nearly equal) the English article title?
import re, collections, unicodedata
data = open('/root/hp/data/enwik9', 'rb').read().decode('utf-8', errors='replace')
pages = data.split('<page>')[1:]
iw_re = re.compile(r'^\[\[([a-z][a-z\-]{1,11}):([^\]\n]*)\]\]\s*$')
n_pages = n_with = n_ent = 0
eq = eq_ci = eq_strip = 0
bytes_ent = bytes_eq = 0
langs = collections.Counter()
per_block = []
def strip_acc(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).lower()
for p in pages:
    n_pages += 1
    t0 = p.find('<title>'); t1 = p.find('</title>')
    title = p[t0 + 7:t1]
    s = p.find('<text xml:space="preserve">'); e = p.find('</text>')
    if s < 0 or e < 0: continue
    lines = p[s:e].split('\n')
    ents = []
    for ln in reversed(lines):
        m = iw_re.match(ln.strip())
        if m: ents.append((m.group(1), m.group(2)))
        elif ln.strip() == '': continue
        else: break
    if not ents: continue
    n_with += 1
    k = 0
    for lang, tt in ents:
        n_ent += 1; langs[lang] += 1
        L = len(lang) + len(tt) + 6
        bytes_ent += L
        if tt == title: eq += 1; bytes_eq += L; k += 1
        elif tt.lower() == title.lower(): eq_ci += 1
        elif strip_acc(tt) == strip_acc(title): eq_strip += 1
    per_block.append((len(ents), k))
print('pages', n_pages, 'pages with interwiki', n_with, 'entries', n_ent)
print('exact title copies', eq, f'{eq/n_ent:.3f}', 'case-insens extra', eq_ci, 'accent-strip extra', eq_strip)
print('entry bytes', bytes_ent, 'bytes in exact copies', bytes_eq)
blocks_with_copy = sum(1 for n, k in per_block if k > 0)
print('blocks with >=1 exact copy', blocks_with_copy)
print('top langs', langs.most_common(25))
