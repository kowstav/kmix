"""I04: causal directed lag predictors against actual lex final byte costs.

Fixed before remote execution: lags 1/2/4/8/16/64, 8192 shared rows, 32 edges/row,
gamma32, rank pseudocount64, fixed lag mixture 1/2,1/4,1/8,1/16,1/32,1/32. All syntax,
case, escape and partial EOF outcomes are charged. This is an additive root
expert likelihood screen, not a native archive or a globally normalized P0 tilt.
"""
import argparse
import collections
import hashlib
import json
import pathlib
import re
import time
import types

import numpy as np
from research_round7_wrt import inverse_byte, load_dictionary
from research_round7_field_screen import literal_wrt, SEP, TEND
from research_round7_word_association_screen import Mixture

LAGS = (1, 2, 4, 8, 16, 64)
ROW_CAP = 8192
EDGE_CAP = 32
GAMMA = 32
RANK_PSEUDOCOUNT = 64
RESCALE_AT = 1 << 20
LAG_WEIGHTS = (.5, .25, .125, .0625, .03125, .03125)
INPUT_SHA256 = {
    'a': 'e3cf8c63ac7bbc246587bd09729b89abf6bbebc718a1643013cfec57b1892292',
    'b': 'c42695d3600f06a7525a5450a9cfa0044b52e7413344f75fcec28ed46c6781cd',
    'c': '39b2ac6b5f9fbdacdb70778b5d9f5cd14e92d683b8b10688a8ab4e7031b20d9f',
    'd': 'e540a24ded0810ba4fbe4647f267fae38651371d9574e05a7897ed92822e86db',
}
COST_SHA256 = {
    'a': 'f95d1f44ba57bc19bbb348a687d4f89a77ea9edf4b1b7ddf7f920abb2b420444',
    'b': '22a66df7f9cd46e0883f3234dc5f0db6af173bf342d31a9db49fd9174dc46235',
    'c': '4fa91d9fe5e8766ee0f3adc0d1fa9f10eb6e3d955df1f69367de61519b6e9533',
    'd': '580cdd9e22d5a45fbd596a6ba4d9999bb0c8d451509a70fdef03c86fa047101f',
}


class Row:
    def __init__(self):
        self.counts = {}
        self.total = 0

    def add(self, w, cap):
        removed = 0
        if w not in self.counts and len(self.counts) >= cap:
            victim = min(self.counts, key=lambda v: (self.counts[v], v))
            removed = self.counts.pop(victim)
            self.total -= removed
        self.counts[w] = self.counts.get(w, 0) + 1
        self.total += 1
        rescaled = self.total >= RESCALE_AT
        if rescaled:
            self.counts = {v: (c + 1) // 2 for v, c in self.counts.items()}
            self.total = sum(self.counts.values())
        return removed, rescaled


class Words:
    def __init__(self, codes, spellings, row_cap=ROW_CAP, edge_cap=EDGE_CAP):
        if not codes or len(codes) != len(spellings):
            raise ValueError('Invalid dictionary')
        if row_cap < 1 or edge_cap < 1:
            raise ValueError('Invalid memory bounds')
        self.rank = 1 / (np.arange(len(codes), dtype=np.float64) + 16)
        self.rank /= self.rank.sum()
        self.global_counts = np.ones(len(codes), np.int64)
        self.global_total = 0
        self.rows = collections.OrderedDict()
        self.row_cap, self.edge_cap = row_cap, edge_cap
        self.family_names = ['rank_prior', 'global_rank64'] + [
            'directed_gap%d_gamma32' % d for d in LAGS] + ['directed_fixed_lag_mix']
        self.stats = {'observed_pairs': [0] * len(LAGS), 'row_evictions': 0,
                      'discarded_row_counts': 0, 'edge_evictions': 0,
                      'discarded_edge_counts': 0, 'row_rescales': 0}
        self.reset()

    def reset(self):
        # A decoded article boundary clears sources, not the learned past.
        self.recent = collections.deque(maxlen=max(LAGS))
        self.article = types.SimpleNamespace(counts=collections.Counter())
        self.article_events = 0
        self.in_title = True

    def predictions(self, w):
        prior = (self.global_counts[w] - 1 + RANK_PSEUDOCOUNT * self.rank[w]) / (
            self.global_total + RANK_PSEUDOCOUNT)
        result = [self.rank[w], prior]
        for j, d in enumerate(LAGS):
            row = self.rows.get((j, self.recent[-d])) if len(self.recent) >= d else None
            result.append((row.counts.get(w, 0) + GAMMA * prior) / (row.total + GAMMA)
                          if row is not None else prior)
        result.append(sum(a * p for a, p in zip(LAG_WEIGHTS, result[2:])))
        return np.asarray(result, np.float64)

    def prefix_predictions(self, ids):
        return sum((self.predictions(w) for w in ids), np.zeros(len(self.family_names)))

    def update(self, w):
        # Every source is in the completed prefix; insert the target only now.
        for j, d in enumerate(LAGS):
            if len(self.recent) < d:
                continue
            key = (j, self.recent[-d])
            if key not in self.rows:
                if len(self.rows) >= self.row_cap:
                    _, old = self.rows.popitem(last=False)
                    self.stats['row_evictions'] += 1
                    self.stats['discarded_row_counts'] += old.total
                self.rows[key] = Row()
            row = self.rows[key]
            removed, rescaled = row.add(w, self.edge_cap)
            self.stats['observed_pairs'][j] += 1
            self.stats['edge_evictions'] += int(removed > 0)
            self.stats['discarded_edge_counts'] += removed
            self.stats['row_rescales'] += int(rescaled)
            self.rows.move_to_end(key)  # Reads never change LRU or counters.
        self.global_counts[w] += 1
        self.global_total += 1
        self.article.counts[w] += 1
        self.article_events += 1
        self.recent.append(w)

    def state(self):
        return {'global_counts': self.global_counts.tolist(), 'global_total': self.global_total,
                'recent': list(self.recent), 'article': sorted(self.article.counts.items()),
                'rows': [(k, sorted(v.counts.items()), v.total) for k, v in self.rows.items()],
                'stats': self.stats.copy()}

    def memory(self):
        return {'active_rows': len(self.rows),
                'active_edges': sum(len(r.counts) for r in self.rows.values()),
                'row_cap_total_across_lags': self.row_cap, 'edge_cap_per_row': self.edge_cap,
                'maximum_edge_payload_bytes_u16_id_u32_count': self.row_cap * self.edge_cap * 6,
                'maximum_row_key_payload_bytes_u8_lag_u16_source_u32_total': self.row_cap * 7,
                'excluded_from_payload_estimate': 'row LRU/free slots/hash index/global counts/queue/alignment/code',
                'stats': self.stats}


def peak_rss():
    try:
        import resource
    except ImportError:
        return None
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def screen(raw, cost, dictionary):
    started = time.monotonic()
    if len(raw) != len(cost) or not np.all(np.isfinite(cost)) or np.any(cost < 0):
        raise ValueError('Incomplete or invalid baseline costs')
    codes = list(dictionary)
    ids = {c: i for i, c in enumerate(codes)}
    sep, tend = literal_wrt(SEP, dictionary), literal_wrt(TEND, dictionary)
    first = raw.find(sep)
    if first < 0:
        raise ValueError('No completed article synchronization marker')
    i = offset = first + len(sep)
    words = Words(codes, list(dictionary.values()))
    mix = Mixture(words.family_names)
    markers = sorted([(m.end(), 'start') for m in re.finditer(re.escape(sep), raw)] +
                     [(m.end(), 'end') for m in re.finditer(re.escape(tend), raw)])
    marker, previous, atoms, events = 0, 3, 0, 0
    classes, trace = {}, hashlib.sha256()
    prefix = np.r_[0., np.cumsum(cost, dtype=np.float64)]
    while i < len(raw):
        lo = i
        while marker < len(markers) and markers[marker][0] <= lo:
            if markers[marker][1] == 'start':
                words.reset()
            else:
                words.in_title = False
            marker += 1
        ctx = (previous, 0 if words.article_events < 16 else 1 if words.article_events < 64 else
               2 if words.article_events < 256 else 3)
        c = inverse_byte(raw[i])
        i += 1
        w, cut, probs = None, False, np.zeros(len(words.family_names))
        if c == 12:
            if i < len(raw):
                i += 1
                cls = 'literal_escape'
            else:
                cut, cls = True, 'cut_escape_prefix'
        elif c >= 128:
            code = [c]
            if c > 207:
                if i == len(raw):
                    cut = True
                else:
                    c2 = inverse_byte(raw[i]); code.append(c2); i += 1
                    if c2 > 207:
                        if i == len(raw):
                            cut = True
                        else:
                            code.append(inverse_byte(raw[i])); i += 1
            code = bytes(code)
            if cut:
                probs = words.prefix_predictions([j for j, s in enumerate(codes) if s.startswith(code)])
                cls = 'cut_dictionary_prefix'
            else:
                if code not in ids:
                    raise ValueError('Invalid complete dictionary code at %d' % lo)
                w = ids[code]
                probs = words.predictions(w)
                cls = ('first_in_slice' if words.global_counts[w] == 1 else
                       'known_first_in_article' if w not in words.article.counts else 'article_repeat')
                atoms += 1
        else:
            cls = 'literal_syntax_or_case'
        baseline, before = float(prefix[i] - prefix[lo]), mix.total_gain
        mix.score(probs, baseline, ctx)
        row = classes.setdefault(cls, {'events': 0, 'baseline_bits': 0., 'saving_bytes': 0.})
        row['events'] += 1; row['baseline_bits'] += baseline
        row['saving_bytes'] += (mix.total_gain - before) / 8
        trace.update(np.asarray([lo, *ctx, *probs], '<f8').tobytes())
        if w is not None:
            words.update(w)
            previous = 2
        else:
            previous = (0 if c in (32, 9, 10, 13) else 1 if c in (7, 64) else
                        4 if 65 <= c <= 90 or 97 <= c <= 122 else 3)
        events += 1
        if events % 200000 == 0:
            print(json.dumps({'events': events, 'position': i, 'saving_bytes': mix.total_gain / 8,
                              'wall_seconds': time.monotonic() - started}), flush=True)
        if cut:
            break
    if abs(sum(v['baseline_bits'] for v in classes.values()) - (prefix[-1] - prefix[offset])) >= 1e-5:
        raise AssertionError('Uncharged post-marker bytes')
    return {'experiment': 'I04_directed_lag_v1', 'raw_bytes': len(raw),
            'baseline_ideal_bytes': float(prefix[-1] / 8), 'unscored_prefix_bytes': offset,
            'dictionary_atoms': atoms, 'score': mix.result(), 'by_class': classes,
            'lags_in_completed_DICT_events': LAGS, 'fixed_lag_weights': LAG_WEIGHTS,
            'gamma': GAMMA, 'rank_pseudocount': RANK_PSEUDOCOUNT, 'memory': words.memory(),
            'trace_sha256': trace.hexdigest(), 'wall_seconds': time.monotonic() - started,
            'prototype_peak_rss_kbytes_linux_only': peak_rss(),
            'contract': 'Prefix-only additive root expert; all post-marker outcomes and EOF prefixes charged; ideal final-coder likelihood, not archive/package or globally tilted P0',
            'validation': 'A/B/C/D are previously examined screening slices; freeze any promising design before new independent E/F',
            'neural_training': False, 'paid_rental_usd': 0, 'deletions': []}


def tests():
    codes = [bytes([128 + i]) for i in range(6)]
    spellings = [b'no', b'know', b'now', b'king', b'queen', b'on']
    a, b = Words(codes, spellings, 5, 2), Words(codes, spellings, 5, 2)
    for j in range(350):
        for m in (a, b):
            before = json.dumps(m.state(), sort_keys=True)
            p = sum((m.predictions(w) for w in range(6)), np.zeros(len(m.family_names)))
            assert np.allclose(p, 1., atol=1e-12, rtol=0), p
            assert json.dumps(m.state(), sort_keys=True) == before, 'Prediction mutated state'
            m.update((j * j + j // 3) % 6)
            assert len(m.rows) <= 5 and all(len(r.counts) <= 2 and r.total == sum(r.counts.values()) for r in m.rows.values())
        assert a.state() == b.state(), 'Nondeterministic update/eviction'
    assert a.stats['row_evictions'] > 0
    r = Row()
    for w in [1, 1, 2, 2, 3]:
        r.add(w, 2)
    assert r.counts == {2: 2, 3: 1} and r.total == 3
    r.counts, r.total = {0: RESCALE_AT - 2, 1: 1}, RESCALE_AT - 1
    _, rescaled = r.add(0, 2)
    assert rescaled and r.total == sum(r.counts.values())
    past = [(k, v.total) for k, v in a.rows.items()]
    a.reset()
    assert not a.recent and not a.article.counts and past == [(k, v.total) for k, v in a.rows.items()]
    p = a.predictions(0)
    assert np.allclose(p[2:], p[1], atol=1e-15, rtol=0), 'Unavailable lag must use global fallback'
    # Exact directed relation learned in the prefix; direction is not symmetrized.
    d = Words(codes, spellings)
    for _ in range(40):
        d.reset(); d.update(0); d.update(1)
    d.reset(); d.update(0)
    assert d.predictions(1)[2] > d.predictions(1)[1]
    assert (0, 1) not in d.rows, 'Cross-article transition leaked'
    fixture = {bytes([128]): b'page', bytes([129]): b'title',
               bytes([240, 128]): b'pear', bytes([240, 208, 128]): b'fruit'}
    sep = literal_wrt(SEP, fixture)
    base = sep + b' ' + bytes([240, 128]) + b' '
    for tail in [b'', bytes([240]), bytes([240, 208]), bytes([12]), bytes([12, 255])]:
        raw = base + tail
        result = screen(raw, np.full(len(raw), 8., np.float32), fixture)
        assert result['score']['baseline_suffix_bits'] == (len(raw) - len(sep)) * 8
    print(json.dumps({'self_tests': 'PASS', 'checked': ['normalization', 'pure prediction reads',
          'deterministic row/edge eviction', 'discarded-count normalization', 'rescaling',
          'article source reset with retained learning', 'directed lag causality', 'mixed code/escape EOF costs']}), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--root', default='/kaggle/working/hp_round7')
    args = ap.parse_args()
    tests()
    if args.self_test:
        return
    out = pathlib.Path(args.root)
    paths = {n: (out / 'preserved/slices' / (n + '2m.bin') if n in 'ab' else out / (n + '2m.bin')) for n in 'abcd'}
    costs = {n: out / 'lex_native_2m' / (n + '_cost.f32') for n in 'abcd'}
    dp = out / 'preserved/gen/.dict'
    if not dp.is_file() or any(not p.is_file() or p.stat().st_size != 2000000 for p in paths.values()) or any(not p.is_file() or p.stat().st_size != 8000000 for p in costs.values()):
        raise ValueError('Preserved dictionary/complete matched 2M inputs and byte costs required')
    for n in 'abcd':
        assert hashlib.sha256(paths[n].read_bytes()).hexdigest() == INPUT_SHA256[n], ('Input drift', n)
        assert hashlib.sha256(costs[n].read_bytes()).hexdigest() == COST_SHA256[n], ('Baseline cost drift', n)
    assert hashlib.sha256(dp.read_bytes()).hexdigest() == '4c8568cca9343b9a6212477880f56f8efd162f8784224a25edd043097d36215a', 'Dictionary drift'
    dest = out / 'idea_arch_directed_lag_v1'
    dest.mkdir(exist_ok=False)
    dictionary, rows = load_dictionary(dp), []
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [pathlib.Path(__file__),
              out / 'research_round7_word_association_screen.py', out / 'research_round7_field_screen.py', out / 'research_round7_wrt.py']}
    for n in 'abcd':
        raw, cp = paths[n].read_bytes(), costs[n]
        result = screen(raw, np.fromfile(cp, '<f4'), dictionary)
        result.update(slice=n, input_sha256=hashlib.sha256(raw).hexdigest(),
                      cost_sha256=hashlib.sha256(cp.read_bytes()).hexdigest(),
                      dictionary_sha256=hashlib.sha256(dp.read_bytes()).hexdigest(), source_hashes=hashes)
        (dest / (n + '.json')).write_text(json.dumps(result, indent=2))
        rows.append({'slice': n, 'saving_bytes': result['score']['prequential_saving_bytes'], 'wall_seconds': result['wall_seconds']})
        (dest / 'summary.json').write_text(json.dumps(rows, indent=2))
        print(json.dumps(rows[-1]), flush=True)
    print('DIRECTED_LAG_SCREEN_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
