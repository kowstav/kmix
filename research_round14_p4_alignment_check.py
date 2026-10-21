"""P4 alignment proof: independent re-serialization of the PHDA9 tail vs the causal parser.

Run on Kaggle after structx_lex_scan: python3 this.py <stream.wrt> <english.dic> <records.tsv> <out.json>
1. Rebuilds the lexical dictionary codes exactly as src/preprocess/dictionary.cpp (80 one-byte,
   3,840 two-byte, 40,960 three-byte codes) and decodes every tail line with an independent
   decoder (escape 0x0C, case markers 0x40/0x07/0x06, remapped 'L','N','J','K' -> '<','>',':',';').
2. Parses the plain-text PHDA9 record grammar independently (revision>, id>, timestamp>,
   contributor>, username>/ip>, id>, /contributor>, >delta; interlanguage [lang:title]).
3. Requires every parser record (offset, kind) to coincide with the reference, and every
   timestamp line to decode to timestamp>DD..:SS.. exactly. Reports any mismatch; never repairs.
"""
import json, re, sys
from pathlib import Path

stream, dic, records, out = map(Path, sys.argv[1:5])
words, line = [], bytearray()
for c in dic.read_bytes():
    if 97 <= c <= 122: line.append(c)
    elif line: words.append(bytes(line)); line = bytearray()
if line: words.append(bytes(line))
rev = {}
for i, w in enumerate(words):
    if i < 80: code = (0x80 + i,)
    elif i < 80 + 3840: j = i - 80; code = (0xD0 + j // 80, 0x80 + j % 80)
    elif i < 80 + 3840 + 40960: j = i - 3920; code = (0xF0 + (j // 80) // 32, 0xD0 + (j // 80) % 32, 0x80 + j % 80)
    else: break
    rev[code] = w
REMAP = {ord('L'): b'<', ord('N'): b'>', ord('J'): b':', ord('K'): b';'}


def decode(b):
    out, i, cap, upper = bytearray(), 0, False, False
    while i < len(b):
        c = b[i]
        if c == 0x0C: out.append(b[i + 1]); i += 2; continue
        if c == 0x40: cap = True; i += 1; continue
        if c == 0x07: upper = True; i += 1; continue
        if c == 0x06: upper = False; i += 1; continue
        if c >= 0x80:
            if c <= 0xCF: code = (c,); i += 1
            elif c <= 0xEF: code = (c, b[i + 1]); i += 2
            elif 0x80 <= b[i + 1] <= 0xCF: code = (c, b[i + 1]); i += 2
            else: code = (c, b[i + 1], b[i + 2]); i += 3
            w = rev[code]
            if upper: w = w.upper()
            elif cap: w = w[:1].upper() + w[1:]
            out += w; cap = False; continue
        out += REMAP.get(c, bytes([c])); i += 1
    return bytes(out)


data = stream.read_bytes()
rev_start = data.find(b'\n\xdf\x99N\n') + 1
il_end = data.rfind(b'L/\xdf\xa7N\n') + len(b'L/\xdf\xa7N\n')
ref, state, errors, decoded_lines = {}, 0, [], 0
pos = rev_start
TS = re.compile(rb'^timestamp>0\d+:\d+$')
while pos < il_end:
    nl = data.find(b'\n', pos); raw = data[pos:nl]
    try:
        t = decode(raw); decoded_lines += 1
    except (KeyError, IndexError) as e:
        errors.append({'offset': pos, 'error': repr(e)}); t = None
    if t is not None:
        if t == b'revision>': state = 1
        elif state == 1 and re.fullmatch(rb'id>\d+', t): ref[pos] = 'I'; state = 2
        elif state == 2 and t.startswith(b'timestamp>'):
            ref[pos] = 'T'; state = 3
            if not TS.fullmatch(t): errors.append({'offset': pos, 'error': 'timestamp grammar', 'text': t[:60].decode('latin1')})
        elif state == 3 and t.startswith(b'username>'): ref[pos] = 'U'; state = 4
        elif state == 4 and re.fullmatch(rb'id>\d+', t): ref[pos] = 'I'; state = 3
        elif t.startswith(b'[') and raw.startswith(b'['): ref[pos] = 'W'; state = 0
    pos = nl + 1
scan = {}
for l in records.read_text().splitlines():
    off, kind, st, valid, hexline = l.split('\t')
    if rev_start <= int(off) < il_end: scan[int(off)] = kind
only_ref = sorted(set(ref) - set(scan)); only_scan = sorted(set(scan) - set(ref))
kind_mismatch = [o for o in set(ref) & set(scan) if ref[o] != scan[o]]
res = {'tail_start': rev_start, 'tail_end': il_end, 'decoded_lines': decoded_lines, 'reference_records': len(ref),
       'parser_records': len(scan), 'by_kind_reference': {k: sum(1 for v in ref.values() if v == k) for k in 'TUIW'},
       'by_kind_parser': {k: sum(1 for v in scan.values() if v == k) for k in 'TUIW'},
       'only_reference': len(only_ref), 'only_parser': len(only_scan), 'kind_mismatch': len(kind_mismatch),
       'examples_only_reference': only_ref[:10], 'examples_only_parser': only_scan[:10], 'decode_or_grammar_errors': errors[:20],
       'error_count': len(errors)}
res['status'] = 'PASS_EXACT_CURSOR_ALIGNMENT' if not (only_ref or only_scan or kind_mismatch or errors) else 'FAIL_ALIGNMENT_MISMATCH'
out.write_text(json.dumps(res, indent=2)); print(json.dumps(res, indent=1)[:4000])
