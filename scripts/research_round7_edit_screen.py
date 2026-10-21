#!/usr/bin/env python3
"""Causal copy/edit probability screens; frozen final-coder costs are the fallback.

This is a likelihood experiment, not a submission archive. The finite state
expert copies an already decoded donor, allowing deletion, insertion and
substitution, then falls back to the original coder at donor exhaustion.
All donor selection, resets and memory writes use decoded prefixes only.
No target-informed alignment, best-donor selection or free edit flags occur.
"""
import argparse
import json
import math
import os
import ctypes
from collections import defaultdict
from pathlib import Path

import numpy as np
try:
    from scipy.signal import lfilter
except ImportError:
    def lfilter(b, a, v):
        # Portable fallback for local verification; Kaggle's SciPy is faster.
        out = v.copy()
        for j in range(1, len(out)):
            out[j] -= a[1] * out[j - 1]
        return out

import research_round7_field_screen as F
from research_round7_wrt import decode_wrt, load_dictionary


# (delete, insert, substitute), chosen before scoring the confirmation slices.
CHANNELS = ((0., 0., 0.), (.001, .001, .01), (.01, .01, .02),
            (.03, .03, .04), (.10, .10, .10), (.25, .15, .15))

_native = None
if os.environ.get('HP_EDIT_KERNEL'):
    _kernel = ctypes.CDLL(os.environ['HP_EDIT_KERNEL'])
    _native = _kernel.hp_edit_logratio
    _native.argtypes = [ctypes.c_char_p, ctypes.c_uint64, ctypes.c_char_p,
                       ctypes.c_uint64, ctypes.POINTER(ctypes.c_double),
                       ctypes.c_double, ctypes.c_double, ctypes.c_double]
    _native.restype = ctypes.c_double


def edit_logratio(observed, donor, costs, rates):
    """Forward marginal over ALL edit paths, with a normalized emission law.

    Each interior state j deletes donor[j] with d, emits fallback without an
    advance with i, substitutes with u, or copies with c=1-d-i-u. State m is
    absorbing fallback. The deletion closure is a geometric causal filter.
    The caller supplies q(actual byte | actual past) from the final coder.
    """
    d, ins, sub = rates
    cp = 1. - d - ins - sub
    if min(d, ins, sub, cp) < 0 or d >= 1:
        raise ValueError('Invalid channel probabilities')
    if _native:
        cs = np.ascontiguousarray(costs, np.float64)
        return _native(observed, len(observed), donor, len(donor),
                       cs.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), d, ins, sub)
    m = len(donor)
    v = np.zeros(m + 1, np.float64)
    v[0] = 1.
    symbols = np.frombuffer(donor, np.uint8)
    gain = 0.
    for b, cost in zip(observed, costs):
        q = math.exp2(-float(cost))
        closed = lfilter([1.], [1., -d], v) if d else v
        nxt = np.zeros_like(v)
        nxt[:m] = ins * q * closed[:m]
        nxt[1:] += (sub * q + cp * (symbols == b)) * closed[:m]
        nxt[m] += q * closed[m]
        z = float(nxt.sum())
        if z <= 0:
            return -math.inf
        gain += math.log2(z) + float(cost)
        v = nxt / z
    return gain


class EditScore(F.Score):
    def __init__(self, name, priors, total_bits, channels=CHANNELS):
        super().__init__(name, priors, total_bits)
        self.channels = channels
        self.models = [(float(a), rates) for a in priors for rates in channels
                       if a > 0]  # keep exactly ONE neutral model
        self.models.insert(0, (0., channels[0]))
        self.fixed_gain = np.zeros(len(self.models), np.float64)
        self.edit_parameters = len(self.models)
        self.model_post = {}
        self.positive_events = 0
        self.oracle_gain = 0.

    def complete(self, ev, end, raw, prefix_cost, status):
        assert self.active is ev
        assert 0 <= ev.start < end <= len(raw)
        observed = raw[ev.start:end]
        costs = np.diff(prefix_cost[ev.start:end + 1])
        baseline = float(prefix_cost[end] - prefix_cost[ev.start])
        if hasattr(ev, '_edit_ratios'):
            ratios = ev._edit_ratios
        else:
            ratios = []
            for rates in self.channels:
                ratios.append(F.log2sum([math.log2(c.weight) +
                    edit_logratio(observed, c.raw, costs, rates) for c in ev.candidates]))
            ev._edit_ratios = ratios
        gains = np.zeros(len(self.models), np.float64)
        for j, (alpha, rates) in enumerate(self.models):
            if alpha:
                lr = ratios[self.channels.index(rates)]
                gains[j] = F.log2sum((math.log2(1 - alpha), math.log2(alpha) + lr))
        # Context is prefix-known and deliberately coarse; no key-per-field
        # retrospective fit. The universal sequence mixture pays startup regret.
        context = (ev.branch,) + tuple(ev.context)
        lp = self.model_post.setdefault(context, np.zeros(len(gains), np.float64))
        pg = F.log2sum((lp + gains).tolist()) - F.log2sum(lp.tolist())
        lp += gains
        lp -= lp.max()
        self.prequential_gain += pg
        self.fixed_gain += gains
        self.oracle_gain += max(0., float(gains.max()))
        self.positive_events += int(pg > 0)
        self.events += 1
        self.matched += int(any(c.raw == observed for c in ev.candidates))
        self.bytes += end - ev.start
        self.covered_bits += baseline
        r = self.by[ev.branch]
        r['events'] += 1
        r['matched'] += int(any(c.raw == observed for c in ev.candidates))
        r['coded_bytes'] += end - ev.start
        r['baseline_bits'] += baseline
        r['prequential_gain_bits'] += pg
        self.active = None
        if self.name == 'combined' and self.events % 10000 == 0:
            print(json.dumps({'progress_events': self.events,
                              'encoded_position': end,
                              'combined_saving_bytes': self.prequential_gain / 8.}), flush=True)
        return {'baseline_bits': baseline, 'prequential_gain_bits': pg,
                'best_channel_gain_bits_unpaid_oracle': float(gains.max()),
                'status': status}

    def result(self):
        return {'name': self.name, 'events': self.events,
            'exact_match_events': self.matched, 'positive_events': self.positive_events,
            'coded_bytes_covered': self.bytes, 'baseline_bits_covered': self.covered_bits,
            'prequential_saving_bytes': self.prequential_gain / 8.,
            'prequential_total_bits': self.total_bits - self.prequential_gain,
            'oracle_best_per_event_saving_bytes_UNPAID': self.oracle_gain / 8.,
            'context_count': len(self.model_post), 'model_count_per_context': len(self.models),
            'fixed_models': [{'alpha': a, 'delete_insert_substitute': rates,
                              'saving_bytes': float(g / 8.)}
                             for (a, rates), g in zip(self.models, self.fixed_gain)],
            'by_branch': dict(self.by)}


class BalancedParser(F.Parser):
    """Keep nested templates and link-bearing parent fields intact.

    Parsing is only an expert trigger. It is never used to reconstruct or alter
    text. Misclassified syntax still has a normalized fallback probability.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bracket_depth = 0
        self.schema_only = False

    def reset_structures(self, now):
        super().reset_structures(now)
        self.bracket_depth = 0

    def finish_value(self, t, i, terminal, complex_reason=False):
        self.scores.finish(t.event, self.end_pos(i), 'balanced_delimiter')
        t.event = None
        if t.key and t.name:
            value = self.span(t.value_start, i)
            if value is not None and len(value) <= 512:
                self.memory.add((t.name, t.key), value, self.end_pos(i))
                self.stats['balanced_named_fields_completed'] += 1

    def template_char(self, i, c):
        # Parent template delimiters inside a link are literal field content.
        if c == 91:
            self.bracket_depth += 1
            return
        if c == 93:
            self.bracket_depth = max(0, self.bracket_depth - 1)
            return
        if self.bracket_depth:
            return
        if c == 123:
            if len(self.templates) >= self.max_depth:
                self.stats['template_depth_limit'] += 1
                self.reset_structures(self.end_pos(i))
            else:
                self.templates.append(F.Template(i + 1))
                self.stats['template_openers'] += 1
            return
        if not self.templates:
            return
        t = self.templates[-1]
        if c == 125:
            if t.mode == 'value':
                self.finish_value(t, i, c)
            self.templates.pop()
            return
        if t.mode == 'name':
            if c == 124:
                t.name = self.key(self.text[t.name_start:i])
                t.mode, t.key_start = 'key', i + 1
            elif i - t.name_start > 256:
                t.mode = 'invalid'
        elif t.mode == 'key':
            if c == 61:
                t.key = self.key(self.text[t.key_start:i])
                t.value_start, t.value_raw_start = i + 1, self.end_pos(i)
                t.mode = 'value'
                donors = self.memory.get((t.name, t.key)) if t.name and t.key else ()
                candidates = []
                z = sum(.5 ** j for j in range(len(donors)))
                for j, (value, available_at) in enumerate(donors):
                    for terminal, w in ((124, .8), (125, .2)):
                        candidates.append(F.Candidate(value + F.literal_wrt_byte(terminal),
                            (.5 ** j / z) * w, available_at))
                t.event = self.scores.begin('schema_value', t.value_raw_start,
                    candidates, ('balanced', min(len(donors), 2)))
                self.stats['named_field_starts'] += 1
            elif c == 124:
                self.stats['positional_fields_skipped'] += 1
                t.key_start = i + 1
            elif i - t.key_start > 256:
                t.mode = 'invalid'
        elif t.mode == 'value' and c == 124:
            self.finish_value(t, i, c)
            t.mode, t.key_start, t.key = 'key', i + 1, b''

    def char(self, i, c):
        # Replicate the conservative article/title/tag framing, while updating
        # balanced syntax for every body character rather than skipping links.
        self.recent.append(c)
        if len(self.recent) > 64:
            del self.recent[:-64]
        if self.recent.endswith(F.SEP):
            self.reset_structures(self.end_pos(i))
            self.article_open = False
            self.title_start = i + 1
            self.title = self.title_raw = b''
            self.stats['article_title_openers'] += 1
            return
        if self.title_start is not None:
            if self.recent.endswith(F.TEND):
                b = i + 1 - len(F.TEND)
                value = self.span(self.title_start, b)
                if value is not None and 0 < len(value) <= 4096:
                    self.title_raw, self.title = value, self.text[self.title_start:b]
                    self.title_available = self.end_pos(i)
                    self.stats['titles_captured'] += 1
                self.title_start = None
                self.article_open = True
                self.in_tag = False
                self.tag.clear()
            elif i - self.title_start > 4096:
                self.title_start = None
            return
        if not self.article_open:
            return
        if c == 60 and not self.in_tag:
            self.in_tag = True
            self.tag = bytearray([c])
            return
        if self.in_tag:
            if c != 60:
                self.tag.append(c)
            if c == 62:
                if bytes(self.tag) == b'</page>':
                    self.reset_structures(self.end_pos(i))
                    self.article_open = False
                self.in_tag = False
                self.tag.clear()
            elif len(self.tag) > 512:
                self.in_tag = False
                self.tag.clear()
            return
        self.template_char(i, c)
        if not self.schema_only:
            self.link_char(i, c)

    def run(self):
        # F.Parser.run also proposes prefix-gated title repetitions. Keeping it
        # makes this directly comparable with the earlier exact-copy screen.
        super().run()


def screen(raw, costs, dictionary, event_output=None, mode='balanced'):
    costs = np.asarray(costs)
    if len(costs) != len(raw) or not np.isfinite(costs).all() or (costs < 0).any():
        raise ValueError('Invalid aligned final-coder costs')
    offset = raw.find(F.literal_wrt(F.SEP, dictionary))
    if offset < 0:
        raise ValueError('No article separator to synchronize')
    text, starts, ends, _ = decode_wrt(raw[offset:], dictionary)
    scores = F.Scores(raw, costs, F.DEFAULT_PRIORS, 512, event_output)
    if mode == 'edit':
        scores.scores = {name: EditScore(name, F.DEFAULT_PRIORS, scores.prefix_cost[-1])
                         for name in scores.scores}
    parser = BalancedParser(raw, text, starts, ends, offset, scores)
    parser.run()
    return {'mode': mode, 'raw_bytes': len(raw), 'decoded_bytes': len(text),
        'unscored_prefix_bytes': offset,
        'baseline_ideal_bytes': float(scores.prefix_cost[-1] / 8.),
        'contract': {'measurement': 'ideal likelihood only; package and CPU not included',
                     'donors': 'decoded prefix only, bounded keyed value memory',
                     'expert': 'normalized probabilistic edit channel with frozen base fallback',
                     'selection': 'Bayesian sequence mixture, neutral model included',
                     'oracle': 'diagnostic only; free best-model choices are NOT coded gains'},
        'parser_counts': dict(parser.stats), 'screen_counts': dict(scores.stats),
        'memory': {'keys': len(parser.memory.data), 'payload_bytes': parser.memory.bytes},
        'scores': {k: s.result() for k, s in scores.scores.items()}}


def self_test():
    # Enumerate every byte and compare the forward emission mass with one.
    donor = b'ab'
    for rates in CHANNELS:
        probabilities = [math.exp2(edit_logratio(bytes([b]), donor, [8.], rates)-8.)
                         for b in range(256)]
        assert abs(sum(probabilities)-1) < 1e-12, (rates, sum(probabilities))
    exact = edit_logratio(b'abc', b'abc', [8., 8., 8.], (0., 0., 0.))
    assert exact == 24.
    assert edit_logratio(b'axc', b'abc', [8.] * 3, (0., 0., 0.)) == -math.inf
    assert math.isfinite(edit_logratio(b'axc', b'abc', [8.] * 3, (.01, .01, .02)))
    # Exhausted donors emit fallback, so extra suffixes cannot gain free bits.
    assert edit_logratio(b'abcZZ', b'abc', [8.] * 5, (0., 0., 0.)) == 24.
    # Nested link/template content belongs to the parent's whole field.
    text = (F.SEP + b'First</title><text>{box|country=[Example|Country]'
        b'|extra={x|a=123}|name=One}</text></page>\n' + F.SEP +
        b'Second</title><text>{box|country=[Example|Country]'
        b'|extra={x|a=124}|name=Two}</text></page>')
    raw = bytes(F.inverse_byte(c) for c in text)
    report = screen(raw, np.full(len(raw), 8., np.float32), {})
    assert report['parser_counts']['balanced_named_fields_completed'] == 8
    assert report['scores']['schema_value']['matched_events'] >= 1
    assert report['scores']['combined']['coded_bytes_covered'] <= len(raw)
    print(json.dumps({'self_test': 'passed', 'fixture_events': report['scores']['schema_value']['events']}))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--slice')
    ap.add_argument('--cost')
    ap.add_argument('--dictionary')
    ap.add_argument('--json')
    ap.add_argument('--events-jsonl')
    ap.add_argument('--mode', choices=['balanced', 'edit'], default='edit')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if not all((args.slice, args.cost, args.dictionary, args.json)):
        ap.error('Need --slice --cost --dictionary --json')
    raw = Path(args.slice).read_bytes()
    costs = np.fromfile(args.cost, '<f4')
    dictionary = load_dictionary(args.dictionary)
    with open(args.events_jsonl, 'w') if args.events_jsonl else open(Path(args.json).with_suffix('.events.jsonl'), 'w') as audit:
        result = screen(raw, costs, dictionary, audit, args.mode)
    Path(args.json).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'mode': args.mode, 'bytes': len(raw),
        'parser_counts': result['parser_counts'], 'memory': result['memory'],
        'gains': {k: r['prequential_saving_bytes'] for k, r in result['scores'].items()}}), flush=True)


if __name__ == '__main__':
    main()
