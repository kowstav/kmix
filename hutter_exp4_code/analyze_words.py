"""Phase 1 analyses for the context-miner idea.
A. Vocabulary saturation over enwik8 in original order.
B. Where the archive's bits go (best stack: transformer + classical coder, held-out test).
C. Hard words: how often the answer was minable from text the decoder already had.
"""
import re, json, math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

H = Path('/kaggle/working/hutter_lab')
OUT = H / 'exp4'
OUT.mkdir(exist_ok=True)
W = re.compile(rb'[A-Za-z]+')
rep = {}

# ---------------- A. vocabulary saturation (original enwik8 order) ----------------
raw = (H / 'data/enwik8').read_bytes()
seen = set()
marks = [0.001, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0]
mi = 0
n = len(raw)
tok_total = tok_novel = 0
window_novel = []           # novelty rate per 1% of the file
wn = wt = 0
curve = []
next_pct = 0.01
for m in W.finditer(raw):
    w = m.group()
    tok_total += 1
    wt += 1
    if w not in seen:
        seen.add(w)
        tok_novel += 1
        wn += 1
    while mi < len(marks) and m.start() >= marks[mi] * n:
        curve.append((marks[mi], len(seen)))
        mi += 1
    if m.start() >= next_pct * n:
        window_novel.append((round(next_pct, 2), wn / max(1, wt)))
        wn = wt = 0
        next_pct += 0.01
curve.append((1.0, len(seen)))
V = len(seen)
rep['A_vocab'] = {
    'distinct_words_enwik8': V, 'word_tokens': tok_total, 'novel_token_share_overall': tok_novel / tok_total,
    'distinct_seen_by_fraction_of_file': {f'{f:g}': round(v / V, 4) for f, v in curve},
    'novel_token_rate_in_each_1pct_slice': {f'{p:g}': round(r, 4) for p, r in window_novel[::10]},
}
del seen

# ---------------- B. bits decomposition on the held-out test (best stack) ----------------
E2 = H / 'exp2'
test = (E2 / 'data/test.bin').read_bytes()
train = (E2 / 'data/train.bin').read_bytes()
nt = len(test)
costs = {'transformer': np.load(E2 / 'runs/f288/test_cost.npy').astype(np.float64)}
p = H / 'exp3/cmskel/ar6nn_mix.f32'
if p.exists():
    costs['stack'] = np.fromfile(p, np.float32).astype(np.float64)
train_words = Counter(W.findall(train))
known = set(train_words)
cat = np.zeros(nt, np.int8)        # 0 non-word byte, 1 novel-word letter, 2 known-word first letter, 3 known-word other letters
occ = []
for m in W.finditer(test):
    a, b = m.span()
    w = m.group()
    if w in known:
        cat[a] = 2
        cat[a + 1:b] = 3
    else:
        cat[a:b] = 1
        known.add(w)               # once decoded, it is history for later occurrences
    occ.append((a, b, w))
B = {}
for k, c in costs.items():
    tot = c.sum()
    B[k] = {'bpb': c.mean(), **{name: {'byte_share': float((cat == i).mean()), 'bit_share': float(c[cat == i].sum() / tot),
                                        'bits_per_byte': float(c[cat == i].mean())}
                                 for i, name in enumerate(['non-word bytes', 'letters of never-seen words',
                                                           'first letter of known words', 'other letters of known words'])}}
rep['B_bits'] = B

# ---------------- C. hard words: minable from history? ----------------
ref = 'stack' if 'stack' in costs else 'transformer'
c = costs[ref]
# word-level n-gram tables over the training text (= previously decoded text)
tw = W.findall(train)
big = defaultdict(Counter)
tri = defaultdict(Counter)
for i in range(2, len(tw)):
    big[tw[i - 1]][tw[i]] += 1
    tri[(tw[i - 2], tw[i - 1])][tw[i]] += 1
del tw
stats = Counter()
bits = Counter()
pot = Counter()
prev2 = prev1 = None
for a, b, w in occ:
    wc = float(c[a:b].sum())
    hard = wc >= 8
    if hard:
        stats['hard'] += 1
        bits['hard'] += wc
        uni = train_words.get(w, 0) > 0
        bg = big.get(prev1)
        tg = tri.get((prev2, prev1))
        in_bg = bool(bg) and w in bg
        in_tg = bool(tg) and w in tg
        top1_bg = bool(bg) and bg.most_common(1)[0][0] == w
        rank_bg = None
        if in_bg:
            rank_bg = 1 + sum(1 for v in bg.values() if v > bg[w])
        for key, flag in (('seen_before', uni), ('bigram_seen', in_bg), ('trigram_seen', in_tg), ('bigram_top1', top1_bg),
                          ('bigram_top5', rank_bg is not None and rank_bg <= 5)):
            if flag:
                stats[key] += 1
                bits[key] += wc
        # what an exact n-gram miner could charge: -log2 of its own estimate (trigram > bigram backoff, add-1)
        if in_tg:
            pm = tg[w] / (sum(tg.values()) + 1)
        elif in_bg:
            pm = 0.5 * bg[w] / (sum(bg.values()) + 1)
        else:
            pm = None
        if pm is not None:
            pot['miner_bits'] += -math.log2(pm)
            pot['model_bits'] += wc
            pot['n'] += 1
    # dynamic update with the decoded test text
    if prev1 is not None:
        big[prev1][w] += 1
        if prev2 is not None:
            tri[(prev2, prev1)][w] += 1
    train_words[w] += 1
    prev2, prev1 = prev1, w
tot_bits = c.sum()
rep['C_hard_words'] = {
    'reference': ref, 'hard_threshold_bits': 8, 'hard_occurrences': stats['hard'], 'hard_bits_share_of_all': bits['hard'] / tot_bits,
    **{k: {'occ_share': stats[k] / stats['hard'], 'bits_share_of_hard': bits[k] / bits['hard']} for k in
       ('seen_before', 'bigram_seen', 'trigram_seen', 'bigram_top1', 'bigram_top5')},
    'ngram_miner_on_hard_words_it_covers': {'occurrences': pot['n'], 'model_bits': pot['model_bits'], 'miner_bits': pot['miner_bits'],
                                            'max_saving_share_of_all_bits': max(0.0, pot['model_bits'] - pot['miner_bits']) / tot_bits},
}
(OUT / 'analysis_words.json').write_text(json.dumps(rep, indent=1, default=float))
print(json.dumps(rep, indent=1, default=float))
