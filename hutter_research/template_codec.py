"""Paid constructor-run templates with right-context backoff (P5): exact reversible codec.

Extends constructor_codec without changing it. The paid channels are identical: lexicon,
layout gaps, constructor/literal flags, literal (OOV) words, case. So is the direct
constructor-sequence model (ConditionalModel, coarse left/right/wrong anchor class,
previous-constructor parent, alpha 4).

Each maximal constructor run (consecutive lexicon words, length n, known to the decoder
from the paid flags) chooses either the direct sequence or a template plus at most E
edits. The choice is a paid branch flag in the same range-coded stream:

  direct:   every constructor id coded by the direct model, exactly as constructor_codec;
  template: template id t (adaptive model keyed by (min(n,4), anchor class), with
            backoff to min(n,4) and global), edit count e <= E (adaptive, keyed by min(n,4)),
            then e operations, each with type {sub, ins, del} (adaptive), a position coded
            uniformly over len(template)+1 values, and a symbol (adaptive) for sub/ins.

Ops are applied right to left on template indices, so every position refers to the
original template. After either branch the direct model is updated with the run's ids
under the same contexts. The direct statistics are therefore identical whichever
branch is chosen, and every feature updates only after its target is coded.

The encoder may search every template using the actual run, because branch, id and edit
stream are all paid. The branch is the minimum exact ideal code length under the current
integer frequencies, including the branch flag (ties go to direct).

Dictionaries:
  none   - no branch flag at all. The stream is byte-identical to constructor_codec
           coarse_<ctx>:alpha for the same input (asserted by the harness).
  static - top-K runs (length >= 2) of an ordered run trie ranked by count*(len-1),
           ties by the id sequence; the table is gzip-serialized and PAID in every archive.
  prefix - sequential prefix-built dictionary: after each decoded run of length >= 2 the
           run is inserted, or refreshed if present; when full, the least recently used
           slot is evicted (ties: lowest slot). Identical and future-free in encoder and
           decoder; no table bytes.

Anchor classes come from the content-first literal channel, which is paid before use.
`wrong` is the matched deterministic unrelated-anchor control. Candidate templates
within edit distance E are found with an exact symmetric-deletion index and verified by
dynamic programming.
"""
import gzip
import math
import struct
from itertools import combinations
from .constructor_codec import WORDS, prepare, anchors, context, ConditionalModel, varint, get_varint
from .native_weights import BinEncoder, BinDecoder

CTX = {'left': 'coarse_left', 'right': 'coarse_right', 'wrong': 'coarse_wrong'}
CTX_ID = {'left': 0, 'right': 1, 'wrong': 2}
DICT_ID = {'none': 0, 'static': 1, 'prefix': 2}
MAGIC = b'HPTPL141'
HEADER = '<BBBBHQI8I'
HSIZE = 8 + struct.calcsize(HEADER)
ALPHA = 4


class Uniform:
    def __init__(self, m):
        self.cnt = [1] * m; self.tot = m; self.k = m
    def update(self, s):
        pass


class Restricted:
    """Support restricted to the first `size` symbols of a selected ConditionalModel."""
    def __init__(self, base, size):
        self.base = base; self.cnt = base.cnt[:size]; self.tot = sum(self.cnt); self.k = size
    def update(self, s):
        self.base.update(s)


def probe(model, key):
    """cnt/tot that model.select(key) would produce, without creating contexts."""
    k, alpha = model.k, model.alpha
    z = [0] * k
    g = model.global_counts; c = model.contexts.get(key) or z
    if isinstance(key, tuple):
        par = model.contexts.get(('parent', key[0])) or z
        dp = 2 * sum(par) + k; dg0 = 2 * sum(g) + k
        g = [1 + 16384 * ((2 * x + 1) * dp + (2 * y + 1) * dg0) // (2 * dg0 * dp) for x, y in zip(g, par)]
    dg = 2 * sum(g) + k; dc = 2 * sum(c) + k
    cnt = [1 + 16384 * ((8 - alpha) * (2 * x + 1) * dc + alpha * (2 * y + 1) * dg) // (8 * dg * dc) for x, y in zip(g, c)]
    return cnt, sum(cnt)


def dry_cost(model, keys, syms, size=None):
    """Exact ideal bits of coding syms under keys with sequential updates; no mutation."""
    k, alpha = model.k, model.alpha
    g = list(model.global_counts); store = {}
    def lst(key):
        if key not in store:
            base = model.contexts.get(key); store[key] = list(base) if base is not None else [0] * k
        return store[key]
    bits = 0.0
    for key, s in zip(keys, syms):
        c = lst(key)
        if isinstance(key, tuple):
            par = lst(('parent', key[0]))
            dp = 2 * sum(par) + k; dg0 = 2 * sum(g) + k
            gg = [1 + 16384 * ((2 * x + 1) * dp + (2 * y + 1) * dg0) // (2 * dg0 * dp) for x, y in zip(g, par)]
        else:
            par = None; gg = g
        dg = 2 * sum(gg) + k; dc = 2 * sum(c) + k
        cnt = [1 + 16384 * ((8 - alpha) * (2 * x + 1) * dc + alpha * (2 * y + 1) * dg) // (8 * dg * dc) for x, y in zip(gg, c)]
        tot = sum(cnt[:size]) if size is not None else sum(cnt)
        bits += math.log2(tot / cnt[s])
        for counts in [g, c] + ([par] if par is not None else []):
            counts[s] += 1
            if sum(counts) > 32768:
                counts[:] = [x // 2 for x in counts]
    return bits


def edit_script(t, r, cap):
    """Minimal Levenshtein script turning t into r if distance <= cap, else None.
    Ops are (type, position-in-t, symbol): 0=sub, 1=ins (before t[pos]), 2=del,
    listed right to left so positions always refer to the original t."""
    n, m = len(t), len(r)
    if abs(n - m) > cap:
        return None
    INF = cap + 1
    d = [[INF] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        if i <= cap: d[i][0] = i
    for j in range(m + 1):
        if j <= cap: d[0][j] = j
    for i in range(1, n + 1):
        for j in range(max(1, i - cap), min(m, i + cap) + 1):
            best = d[i - 1][j - 1] + (t[i - 1] != r[j - 1])
            if d[i - 1][j] + 1 < best: best = d[i - 1][j] + 1
            if d[i][j - 1] + 1 < best: best = d[i][j - 1] + 1
            d[i][j] = min(best, INF)
    if d[n][m] > cap:
        return None
    ops = []; i, j = n, m
    while i > 0 or j > 0:   # deterministic backtrace: match/sub, then del, then ins
        if i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + (t[i - 1] != r[j - 1]):
            if t[i - 1] != r[j - 1]: ops.append((0, i - 1, r[j - 1]))
            i -= 1; j -= 1
        elif i > 0 and d[i][j] == d[i - 1][j] + 1:
            ops.append((2, i - 1, None)); i -= 1
        else:
            ops.append((1, i, r[j - 1])); j -= 1
    return ops


def apply_ops(t, ops):
    s = list(t)
    for typ, pos, sym in ops:
        if typ == 0: s[pos] = sym
        elif typ == 1: s.insert(pos, sym)
        else: del s[pos]
    return tuple(s)


def deletion_variants(seq, depth):
    out = {seq}
    n = len(seq)
    for k in range(1, min(depth, n) + 1):
        for idx in combinations(range(n), k):
            drop = set(idx); out.add(tuple(x for i, x in enumerate(seq) if i not in drop))
    return out


class RunTrie:
    """Ordered constructor-run trie with exact multiplicity."""
    def __init__(self):
        self.root = {}
    def insert(self, run, count=1):
        node = self.root
        for s in run: node = node.setdefault(s, {})
        node[None] = node.get(None, 0) + count
    def items(self):
        stack = [((), self.root)]
        while stack:
            prefix, node = stack.pop()
            for key, child in node.items():
                if key is None: yield prefix, child
                else: stack.append((prefix + (key,), child))


def constructor_runs(raw, words=WORDS):
    _, flags, _, _, ids, _ = prepare(raw, words)
    runs, i, n = [], 0, len(flags)
    while i < n:
        if not flags[i]: i += 1; continue
        j = i
        while j < n and flags[j]: j += 1
        runs.append(tuple(ids[i:j])); i = j
    return runs


def select_templates(trie, k):
    items = [(c * (len(r) - 1), r) for r, c in trie.items() if len(r) >= 2]
    items.sort(key=lambda x: (-x[0], x[1]))
    return [r for _, r in items[:k]]


def serialize_table(templates):
    b = bytearray(varint(len(templates)))
    for t in templates: b += varint(len(t)) + bytes(t)
    return bytes(b)


def parse_table(blob, alphabet):
    n, off = get_varint(blob, 0); out = []
    for _ in range(n):
        m, off = get_varint(blob, off); t = tuple(blob[off:off + m]); off += m
        if len(t) != m or m < 2 or any(x >= alphabet for x in t): raise ValueError('invalid template')
        out.append(t)
    if off != len(blob) or len(set(out)) != len(out): raise ValueError('invalid template table')
    return out


class Dictionary:
    def __init__(self, kind, cap, edit_cap, templates=()):
        self.kind, self.cap, self.E = kind, cap, edit_cap
        self.slots = list(templates) if kind == 'static' else []
        self.where = {t: i for i, t in enumerate(self.slots)}
        self.last = [0] * len(self.slots); self.clock = 0; self.index = {}
        for i, t in enumerate(self.slots): self._index(i, t, 1)
    def _index(self, slot, t, sign):
        for v in deletion_variants(t, self.E):
            if sign > 0: self.index.setdefault(v, set()).add(slot)
            else:
                s = self.index.get(v)
                if s is not None:
                    s.discard(slot)
                    if not s: del self.index[v]
    def hits(self, run):
        """Superset of slots within edit distance E (exact symmetric-deletion property)."""
        hits = set()
        for v in deletion_variants(run, self.E):
            s = self.index.get(v)
            if s: hits |= s
        return hits
    def observe(self, run):
        """Post-decode update (prefix kind only); identical in encoder and decoder."""
        if self.kind != 'prefix' or len(run) < 2: return
        self.clock += 1
        if run in self.where:
            self.last[self.where[run]] = self.clock; return
        if len(self.slots) < self.cap:
            slot = len(self.slots); self.slots.append(run); self.last.append(self.clock)
        else:
            slot = min(range(self.cap), key=lambda i: (self.last[i], i))
            old = self.slots[slot]; self._index(slot, old, -1); del self.where[old]
            self.slots[slot] = run; self.last[slot] = self.clock
        self.where[run] = slot; self._index(slot, run, 1)


class Models:
    def __init__(self, alphabet, cap, edit_cap):
        self.direct = ConditionalModel(alphabet, ALPHA)
        self.branch = ConditionalModel(2, ALPHA)
        self.template = ConditionalModel(cap, ALPHA) if cap else None
        self.edits = ConditionalModel(edit_cap + 1, ALPHA) if edit_cap else None
        self.optype = ConditionalModel(3, ALPHA)
        self.symbol = ConditionalModel(alphabet, ALPHA)


def _run_keys(mode, left, right, variables, i, run):
    keys, previous = [], -1
    for r, s in enumerate(run):
        keys.append(context(mode, left[i + r], right[i + r], variables, i + r, previous, r)); previous = s
    return keys


def _template_cost(models, nb, cls, slot, ops, size, E, tcnt, ttot):
    bits = math.log2(ttot / tcnt[slot])
    if E:
        bits += dry_cost(models.edits, [nb], [len(ops)])
        bits += dry_cost(models.optype, [0] * len(ops), [o[0] for o in ops])
        syms = [o[2] for o in ops if o[0] != 2]
        if syms: bits += dry_cost(models.symbol, [0] * len(syms), syms)
        bits += len(ops) * math.log2(size + 1)
    return bits


def encode(raw, ctx='right', kind='none', cap=0, edit_cap=0, templates=None, words=WORDS, stats=None):
    if ctx not in CTX or kind not in DICT_ID or edit_cap not in (0, 1, 2) or cap < 0 or cap > 65535:
        raise ValueError('invalid configuration')
    if (kind == 'none') != (cap == 0) or (kind == 'none' and edit_cap): raise ValueError('none uses cap 0, edit 0')
    if kind == 'static' and (templates is None or len(templates) > cap): raise ValueError('static needs <= cap templates')
    if not words or list(words) != sorted(set(words)) or len(words) > 255: raise ValueError('invalid lexicon')
    mode = CTX[ctx]
    gaps, flags, literals, cases, ids, literal_words = prepare(raw, words)
    left, right, variables = anchors(flags, literal_words)
    alphabet = len(words); enc = BinEncoder(); M = Models(alphabet, cap, edit_cap)
    D = Dictionary(kind, cap, edit_cap, templates or ()) if kind != 'none' else None
    st = stats if stats is not None else {}
    st.update(runs=0, template_runs=0, edits=0, direct_tokens=0)
    i, n = 0, len(flags)
    while i < n:
        if not flags[i]: i += 1; continue
        j = i
        while j < n and flags[j]: j += 1
        run = tuple(ids[i:j]); keys = _run_keys(mode, left, right, variables, i, run); st['runs'] += 1
        choice = None
        if D is not None:
            nb = min(len(run), 4); cls = context(mode, left[i], right[i], variables, i, -1, 0)[1]
            direct_bits = dry_cost(M.branch, [nb], [0]) + dry_cost(M.direct, keys, list(run))
            hits = D.hits(run)
            if hits:
                size = len(D.slots); tkey = (nb, cls); tcnt, _ = probe(M.template, tkey); ttot = sum(tcnt[:size])
                flag_bits = dry_cost(M.branch, [nb], [1]); best_bits = direct_bits
                # Exact search with safe pruning: a slot is skipped only when an unavoidable part
                # of its cost (flag + id, plus one uniform position per required length change)
                # already reaches the best total found so far.
                for tbits, slot in sorted((math.log2(ttot / tcnt[slot]), slot) for slot in hits):
                    if flag_bits + tbits >= best_bits: break
                    tlen = len(D.slots[slot])
                    if flag_bits + tbits + abs(tlen - len(run)) * math.log2(tlen + 1) >= best_bits: continue
                    ops = edit_script(D.slots[slot], run, edit_cap)
                    if ops is None: continue
                    b = flag_bits + _template_cost(M, nb, cls, slot, ops, tlen, edit_cap, tcnt, ttot)
                    if b < best_bits: best_bits = b; choice = (b, slot, ops)
            M.branch.select(nb); enc.encode_adapt(M.branch, 1 if choice else 0)
        if choice is None:
            for key, s in zip(keys, run):
                M.direct.select(key); enc.encode_adapt(M.direct, s)
            st['direct_tokens'] += len(run)
        else:
            _, slot, ops = choice; size = len(D.slots)
            M.template.select((nb, cls)); enc.encode_adapt(Restricted(M.template, size), slot)
            if edit_cap:
                M.edits.select(nb); enc.encode_adapt(M.edits, len(ops))
                tlen = len(D.slots[slot])
                for typ, pos, sym in ops:
                    M.optype.select(0); enc.encode_adapt(M.optype, typ)
                    enc.encode_adapt(Uniform(tlen + 1), pos)
                    if typ != 2: M.symbol.select(0); enc.encode_adapt(M.symbol, sym)
            assert apply_ops(D.slots[slot], ops) == run, 'template self-check failed'
            for key, s in zip(keys, run):
                M.direct.select(key); M.direct.update(s)
            st['template_runs'] += 1; st['edits'] += len(ops)
        if D is not None: D.observe(run)
        i = j
    lex = b'\n'.join(w.encode() for w in words)
    table = gzip.compress(serialize_table(templates), mtime=0) if kind == 'static' else b''
    channels = [gzip.compress(c, mtime=0) for c in [lex, gaps, flags, literals, cases]] + [enc.finish(), table, b'']
    head = struct.pack(HEADER, CTX_ID[ctx], ALPHA, DICT_ID[kind], edit_cap, cap, len(raw), len(flags), *[len(c) for c in channels])
    return MAGIC + head + b''.join(channels)


def decode(archive, words_check=None):
    if archive[:8] != MAGIC or len(archive) < HSIZE: raise ValueError('invalid container')
    ctx_id, alpha, kind_id, edit_cap, cap, length, n, *sizes = struct.unpack_from(HEADER, archive, 8)
    ctx = {v: k for k, v in CTX_ID.items()}.get(ctx_id); kind = {v: k for k, v in DICT_ID.items()}.get(kind_id)
    if ctx is None or kind is None or alpha != ALPHA or edit_cap > 2 or sum(sizes) + HSIZE != len(archive): raise ValueError('invalid header')
    if (kind == 'none') != (cap == 0): raise ValueError('invalid dictionary header')
    off = HSIZE; ch = []
    for size in sizes: ch.append(archive[off:off + size]); off += size
    lex, gaps, flags, literals, cases = [gzip.decompress(c) for c in ch[:5]]
    words = lex.split(b'\n'); alphabet = len(words)
    if not words or alphabet > 255 or words != sorted(set(words)) or len(flags) != n or any(f > 1 for f in flags): raise ValueError('invalid structure')
    if ch[7]: raise ValueError('reserved channel not empty')
    literal_words = []; o = 0
    for flag in flags:
        if flag: literal_words.append(None)
        else:
            size, o = get_varint(literals, o); w = literals[o:o + size]; o += size
            if len(w) != size: raise ValueError('truncated literal')
            literal_words.append(w)
    if o != len(literals) or len(cases) != sum(flags) or any(c > 2 for c in cases): raise ValueError('invalid literal/case channel')
    templates = parse_table(gzip.decompress(ch[6]), alphabet) if kind == 'static' else None
    if kind == 'static' and len(templates) > cap: raise ValueError('table exceeds cap')
    if kind != 'static' and ch[6]: raise ValueError('unexpected table')
    mode = CTX[ctx]; left, right, variables = anchors(flags, literal_words)
    dec = BinDecoder(ch[5]); M = Models(alphabet, cap, edit_cap)
    D = Dictionary(kind, cap, edit_cap, templates or ()) if kind != 'none' else None
    ids = [None] * n; i = 0
    while i < n:
        if not flags[i]: i += 1; continue
        j = i
        while j < n and flags[j]: j += 1
        L = j - i; use_template = False
        if D is not None:
            nb = min(L, 4); cls = context(mode, left[i], right[i], variables, i, -1, 0)[1]
            M.branch.select(nb); use_template = dec.decode_adapt(M.branch) == 1
        if not use_template:
            previous = -1
            for r in range(L):
                M.direct.select(context(mode, left[i + r], right[i + r], variables, i + r, previous, r))
                ids[i + r] = dec.decode_adapt(M.direct); previous = ids[i + r]
        else:
            size = len(D.slots)
            if size == 0: raise ValueError('template branch with empty dictionary')
            M.template.select((nb, cls)); slot = dec.decode_adapt(Restricted(M.template, size))
            ops = []
            if edit_cap:
                M.edits.select(nb); e = dec.decode_adapt(M.edits); tlen = len(D.slots[slot])
                for _ in range(e):
                    M.optype.select(0); typ = dec.decode_adapt(M.optype)
                    pos = dec.decode_adapt(Uniform(tlen + 1)); sym = None
                    if typ != 2: M.symbol.select(0); sym = dec.decode_adapt(M.symbol)
                    ops.append((typ, pos, sym))
            try:
                run = apply_ops(D.slots[slot], ops)
            except IndexError:
                raise ValueError('invalid edit position')
            if len(run) != L or any(x >= alphabet for x in run): raise ValueError('template/run length mismatch')
            previous = -1
            for r, s in enumerate(run):
                M.direct.select(context(mode, left[i + r], right[i + r], variables, i + r, previous, r)); M.direct.update(s)
                ids[i + r] = s; previous = s
        if D is not None: D.observe(tuple(ids[i:j]))
        i = j
    result = bytearray(); o = ci = 0
    for pos in range(n + 1):
        size, o = get_varint(gaps, o); gap = gaps[o:o + size]; o += size
        if len(gap) != size: raise ValueError('truncated layout')
        result += gap
        if pos == n: break
        if not flags[pos]: result += literal_words[pos]
        else:
            w = words[ids[pos]]; c = cases[ci]; ci += 1
            result += w if c == 0 else w[:1].upper() + w[1:] if c == 1 else w.upper()
    if o != len(gaps) or len(result) != length: raise ValueError('invalid reconstruction length')
    return bytes(result)


def inspect_sizes(archive):
    sizes = struct.unpack_from(HEADER, archive, 8)[7:]
    return dict(zip(['lexicon', 'layout', 'flags', 'literals', 'case', 'run_stream', 'template_table', 'reserved'], sizes)) | {'header': HSIZE}
