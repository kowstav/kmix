#!/usr/bin/env python3
"""Causal whole-field copy-mixture screening on ORIGINAL WRT byte costs.

Example:
  python research_round7_field_screen.py --slice a.bin --cost a.cost.f32 \
      --dictionary .dict --json a.field_screen.json

Required cost format: little-endian float32 BITS per original coded byte,
as emitted by LAB_COST in labpatch.py. Input is raw WRT bytes, not vocabulary
indices or expanded text. Results are ideal probability lengths, not a native
archive, and inherit float32 cost-dump rounding. No weights are changed.

Candidates are captured at a prefix-known boundary. Their original encoded
bytes and source availability offsets are retained. All candidate selection,
prior contexts, memory insertion and replacement are prefix-only. A candidate
includes the field terminator; mismatches pay ONE whole-field fallback cost.
Fixed priors and a Bayesian mixture over those priors include a neutral alpha=0.
Independent branch scores must NOT be added: a separate, causal first-active
combined stream prevents overlap. Parsing is deliberately conservative: PHDA
uses single braces/brackets for normal wiki templates/internal links. Named,
flat template fields only are stored; nested/link-bearing fields are not.
"""
import argparse
import heapq
import json
import math
import re
import sys
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from research_round7_wrt import decode_wrt, inverse_byte, load_dictionary


DEFAULT_PRIORS = (0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 0.7, 0.9)
BRANCHES = ("title_selflink", "title_repeat", "link_label", "schema_value")
SEP = b"  <page>\n    <title>"
TEND = b"</title>"


def log2sum(values):
    vals = [v for v in values if v != -math.inf]
    if not vals:
        return -math.inf
    m = max(vals)
    return m + math.log2(sum(2.0 ** (v - m) for v in vals))


def word_byte(c):
    return 65 <= c <= 90 or 97 <= c <= 122 or 48 <= c <= 57 or c >= 128


def literal_wrt(text, dictionary):
    """Encode lower-case tag literals using the exact dictionary code map.

    Only used to locate SEP. It is not a general WRT encoder and refuses
    uppercase text; all SEP words are short exact dictionary words/literals.
    """
    if any(65 <= c <= 90 for c in text):
        raise ValueError("literal_wrt accepts lowercase tag literals only")
    forward = {v: k for k, v in dictionary.items()}
    out = bytearray()
    pos = 0
    for m in re.finditer(rb"[a-z]+", text):
        for c in text[pos:m.start()]:
            if c in (6, 7, 12, 64) or c >= 128:
                out.append(12)
            out.append(c)
        out.extend(forward.get(m.group(), m.group()))
        pos = m.end()
    for c in text[pos:]:
        if c in (6, 7, 12, 64) or c >= 128:
            out.append(12)
        out.append(c)
    return bytes(inverse_byte(c) for c in out)


@dataclass(frozen=True)
class Candidate:
    raw: bytes
    weight: float
    available_at: int


@dataclass
class Event:
    start: int
    branch: str
    context: tuple
    candidates: tuple
    cap: int
    fixed_end: int = None
    observers: list = field(default_factory=list)
    finished: bool = False


class Score:
    def __init__(self, name, priors, total_bits):
        self.name = name
        self.priors = np.asarray(priors, dtype=np.float64)
        self.total_bits = float(total_bits)
        self.fixed_gain = np.zeros(len(priors), dtype=np.float64)
        self.prequential_gain = 0.0
        self.post = {}
        self.active = None
        self.events = self.matched = self.bytes = 0
        self.covered_bits = 0.0
        self.by = defaultdict(lambda: {"events": 0, "matched": 0,
                                      "coded_bytes": 0, "baseline_bits": 0.0,
                                      "prequential_gain_bits": 0.0})

    def complete(self, ev, end, raw, prefix_cost, status):
        assert self.active is ev
        assert 0 <= ev.start < end <= len(raw)
        baseline = float(prefix_cost[end] - prefix_cost[ev.start])
        observed = raw[ev.start:end]
        pe = sum(c.weight for c in ev.candidates if c.raw == observed)
        assert 0.0 <= pe <= 1.0 + 1e-12
        gains = []
        for alpha in self.priors:
            log_base = math.log2(1.0 - float(alpha))
            log_copy = (math.log2(float(alpha)) + math.log2(pe) + baseline
                        if alpha > 0.0 and pe > 0.0 else -math.inf)
            gains.append(log2sum((log_base, log_copy)))
        gains = np.asarray(gains, dtype=np.float64)
        # A causal Bayesian sequence mixture over fixed-alpha field models.
        # log likelihood ratios suffice; common baseline factors cancel.
        context = (ev.branch,) + tuple(ev.context)
        lp = self.post.setdefault(context, np.zeros(len(self.priors), np.float64))
        before = log2sum(lp.tolist())
        pg = log2sum((lp + gains).tolist()) - before
        lp += gains
        lp -= np.max(lp)
        self.fixed_gain += gains
        self.prequential_gain += pg
        self.events += 1
        self.matched += int(pe > 0)
        self.bytes += end - ev.start
        self.covered_bits += baseline
        r = self.by[ev.branch]
        r["events"] += 1
        r["matched"] += int(pe > 0)
        r["coded_bytes"] += end - ev.start
        r["baseline_bits"] += baseline
        r["prequential_gain_bits"] += pg
        self.active = None
        return {"baseline_bits": baseline, "copy_probability": pe,
                "prequential_gain_bits": pg, "status": status}

    def result(self):
        return {
            "name": self.name, "events": self.events, "matched_events": self.matched,
            "coded_bytes_covered": self.bytes, "baseline_bits_covered": self.covered_bits,
            "neutral_total_bits": self.total_bits,
            "prequential_total_bits": self.total_bits - self.prequential_gain,
            "prequential_gain_bits": self.prequential_gain,
            "prequential_saving_bytes": self.prequential_gain / 8.0,
            "context_count": len(self.post),
            "fixed_priors": [{"alpha": float(a), "gain_bits": float(g),
                              "saving_bytes": float(g / 8),
                              "total_bits": self.total_bits - float(g)}
                             for a, g in zip(self.priors, self.fixed_gain)],
            "by_branch": dict(self.by),
        }


class Scores:
    def __init__(self, raw, costs, priors, cap, event_output=None):
        self.raw = raw
        self.prefix_cost = np.empty(len(costs) + 1, dtype=np.float64)
        self.prefix_cost[0] = 0.0
        np.cumsum(costs, dtype=np.float64, out=self.prefix_cost[1:])
        self.scores = {b: Score(b, priors, self.prefix_cost[-1]) for b in BRANCHES}
        self.scores["combined"] = Score("combined", priors, self.prefix_cost[-1])
        self.cap = cap
        self.pending = []
        self.sequence = 0
        self.audit = event_output
        self.stats = defaultdict(int)

    def begin(self, branch, start, candidates, context=(), fixed_len=None):
        # Deduplication and caps use prefix-available bytes, not target similarity.
        grouped = {}
        for c in candidates:
            assert c.available_at <= start, (branch, c.available_at, start)
            if not c.raw or len(c.raw) >= self.cap or c.weight <= 0:
                continue
            if c.raw in grouped:
                old = grouped[c.raw]
                grouped[c.raw] = Candidate(c.raw, old.weight + c.weight,
                                           max(c.available_at, old.available_at))
            else:
                grouped[c.raw] = c
        if not grouped or start >= len(self.raw):
            self.stats[branch + "_no_candidate"] += 1
            return None
        if fixed_len is not None and start + fixed_len > len(self.raw):
            self.stats[branch + "_incomplete_fixed_horizon"] += 1
            return None  # not scored; EOF framing is outside these screens
        z = sum(c.weight for c in grouped.values())
        cs = tuple(Candidate(c.raw, c.weight / z, c.available_at)
                   for c in grouped.values())
        # Do not move a field's cap back to EOF: that would incorrectly score
        # an unclosed, cut field as if it had reached its preset deadline.
        ev = Event(start, branch, context, cs, start + self.cap,
                   start + fixed_len if fixed_len is not None else None)
        for scorer in (self.scores[branch], self.scores["combined"]):
            if scorer.active is None:
                scorer.active = ev
                ev.observers.append(scorer)
            else:
                self.stats[scorer.name + "_overlap_skipped"] += 1
        if not ev.observers:
            return None
        self.sequence += 1
        deadline = ev.fixed_end if ev.fixed_end is not None else ev.cap
        heapq.heappush(self.pending, (deadline, self.sequence, ev))
        return ev

    def finish(self, ev, end, status="delimiter"):
        if ev is None or ev.finished:
            return
        if end <= ev.start:
            raise AssertionError("Nonpositive coded event span")
        end = min(end, ev.cap)
        ev.finished = True
        rows = {}
        for scorer in ev.observers:
            rows[scorer.name] = scorer.complete(ev, end, self.raw, self.prefix_cost, status)
        if self.audit is not None:
            self.audit.write(json.dumps({"start": ev.start, "end": end,
                "branch": ev.branch, "context": ev.context,
                "candidate_lengths": [len(c.raw) for c in ev.candidates],
                "source_availability": [c.available_at for c in ev.candidates],
                "scores": rows}, separators=(",", ":")) + "\n")

    def advance(self, position):
        while self.pending and self.pending[0][0] <= position:
            end, _, ev = heapq.heappop(self.pending)
            self.finish(ev, end, "fixed_horizon" if ev.fixed_end is not None else "cap")

    def eof(self):
        # A variable field cut by a slice boundary has unknown continuation. Do
        # not score the cut field as a completed mismatch or update its posterior.
        for scorer in self.scores.values():
            if scorer.active is not None:
                self.stats[scorer.name + "_incomplete_variable_field"] += 1
                scorer.active = None


class ValueMemory:
    def __init__(self, max_keys=8192, max_bytes=4 << 20, donors=2):
        self.data = OrderedDict()
        self.max_keys, self.max_bytes, self.donors = max_keys, max_bytes, donors
        self.bytes = 0
        self.evictions = 0

    def get(self, key):
        values = self.data.get(key, ())
        if key in self.data:
            self.data.move_to_end(key)
        return tuple(values)

    def add(self, key, raw, available_at):
        if not raw or len(raw) > 1024:
            return
        old = self.data.pop(key, [])
        self.bytes -= sum(len(v[0]) for v in old) + len(key[0]) + len(key[1]) if old else 0
        values = [(raw, available_at)] + [v for v in old if v[0] != raw]
        values = values[:self.donors]
        self.data[key] = values
        self.bytes += sum(len(v[0]) for v in values) + len(key[0]) + len(key[1])
        while len(self.data) > self.max_keys or self.bytes > self.max_bytes:
            k, vals = self.data.popitem(last=False)
            self.bytes -= len(k[0]) + len(k[1]) + sum(len(v[0]) for v in vals)
            self.evictions += 1


@dataclass
class Template:
    name_start: int
    mode: str = "name"
    name: bytes = b""
    key_start: int = 0
    key: bytes = b""
    value_start: int = 0
    value_raw_start: int = 0
    event: Event = None
    complex: bool = False


class Parser:
    def __init__(self, raw, decoded, starts, ends, offset, scores, max_depth=16):
        self.raw, self.text, self.starts, self.ends = raw, decoded, starts, ends
        self.offset, self.scores = offset, scores
        self.recent = bytearray()
        self.title = b""
        self.title_raw = b""
        self.title_available = 0
        self.title_start = None
        self.article_open = False
        self.in_tag = False
        self.tag = bytearray()
        self.link = None
        self.templates = []
        self.memory = ValueMemory()
        self.max_depth = max_depth
        self.stats = defaultdict(int)

    def begin_pos(self, i):
        return self.offset + int(self.starts[i])

    def end_pos(self, i):
        return self.offset + int(self.ends[i])

    def span(self, a, b):
        if a >= b:
            return b""
        lo, hi = self.begin_pos(a), self.end_pos(b - 1)
        if ((a > 0 and self.end_pos(a - 1) > lo) or
                (b < len(self.text) and self.begin_pos(b) < hi)):
            self.stats["ambiguous_encoded_span_rejected"] += 1
            return None
        return self.raw[lo:hi]

    @staticmethod
    def key(text):
        # Decoded key only, already observed. No target-value features.
        text = b" ".join(text.strip().lower().split())
        return text if 0 < len(text) <= 128 and b"\n" not in text else b""

    def title_candidates(self, start):
        if not self.title_raw or len(self.title_raw) > 512:
            return []
        return [Candidate(self.title_raw + literal_wrt_byte(term), w, self.title_available)
                for term, w in ((93, .8), (124, .18), (35, .02))]

    def reset_structures(self, now):
        if self.link:
            self.scores.finish(self.link.get("event"), now, "article_reset")
        for t in self.templates:
            self.scores.finish(t.event, now, "article_reset")
        self.link = None
        self.templates = []

    def finish_value(self, t, i, terminal, complex_reason=False):
        self.scores.finish(t.event, self.end_pos(i),
                           "complex_start" if complex_reason else "delimiter")
        t.event = None
        if not t.complex and not complex_reason and t.key and t.name:
            value = self.span(t.value_start, i)
            if value is not None:
                self.memory.add((t.name, t.key), value, self.end_pos(i))
                self.stats["flat_named_fields_completed"] += 1

    def template_char(self, i, c):
        if c == 123:  # PHDA normal '{{' is a single '{'
            if self.templates:
                p = self.templates[-1]
                if p.mode == "value":
                    self.finish_value(p, i, c, True)
                    p.complex = True
                else:
                    p.mode = "invalid"
            if len(self.templates) >= self.max_depth:
                self.stats["template_depth_limit"] += 1
                self.reset_structures(self.end_pos(i))
            else:
                self.templates.append(Template(i + 1))
                self.stats["template_openers"] += 1
            return
        if not self.templates:
            return
        t = self.templates[-1]
        if c == 125:
            if t.mode == "value":
                self.finish_value(t, i, c)
            self.templates.pop()
            return
        if t.mode == "name":
            if c == 124:
                t.name = self.key(self.text[t.name_start:i])
                t.mode, t.key_start = "key", i + 1
            elif i - t.name_start > 256 or c in (91, 93):
                t.mode = "invalid"
        elif t.mode == "key":
            if c == 61:
                t.key = self.key(self.text[t.key_start:i])
                t.value_start, t.value_raw_start = i + 1, self.end_pos(i)
                t.mode, t.complex = "value", False
                donors = self.memory.get((t.name, t.key)) if t.name and t.key else ()
                candidates = []
                z = sum(.5 ** j for j in range(len(donors)))
                for j, (value, available_at) in enumerate(donors):
                    for terminal, w in ((124, .8), (125, .2)):
                        candidates.append(Candidate(value + literal_wrt_byte(terminal),
                            (.5 ** j / z) * w, available_at))
                t.event = self.scores.begin("schema_value", t.value_raw_start,
                    candidates, ("named", min(len(donors), 2)))
                self.stats["named_field_starts"] += 1
            elif c == 124:
                self.stats["positional_fields_skipped"] += 1
                t.key_start = i + 1
            elif c in (91, 93) or i - t.key_start > 256:
                t.mode = "invalid"
        elif t.mode == "value":
            if c == 124:
                self.finish_value(t, i, c)
                t.mode, t.key_start, t.key = "key", i + 1, b""
            elif c == 91:
                self.finish_value(t, i, c, True)
                t.complex = True

    def link_char(self, i, c):
        if self.link is None:
            if c == 91:
                ev = self.scores.begin("title_selflink", self.end_pos(i),
                    self.title_candidates(self.end_pos(i)),
                    (min(len(self.title_raw) // 8, 7),))
                self.link = {"mode": "target", "start": i + 1, "event": ev}
                self.stats["link_openers"] += 1
            return
        link = self.link
        if link["mode"] == "target":
            if c in (124, 93, 35, 10, 91, 123):
                self.scores.finish(link["event"], self.end_pos(i), "delimiter")
                link["event"] = None
                if c == 124:
                    target = self.span(link["start"], i)
                    candidates = ([Candidate(target + literal_wrt_byte(93), 1.0,
                                             self.end_pos(i))]
                                  if target and len(target) <= 512 else [])
                    link["event"] = self.scores.begin("link_label", self.end_pos(i),
                        candidates, (min(len(target or b"") // 8, 7),))
                    link["mode"] = "label"
                    self.stats["piped_link_labels"] += 1
                elif c in (93, 10):
                    self.link = None
                else:
                    link["mode"] = "other"
        elif link["mode"] == "label":
            if c in (93, 124, 10, 91, 123):
                self.scores.finish(link["event"], self.end_pos(i), "delimiter")
                link["event"] = None
                if c in (93, 10):
                    self.link = None
                else:
                    link["mode"] = "other"
        elif c in (93, 10):
            self.link = None

    def char(self, i, c):
        self.recent.append(c)
        if len(self.recent) > 64:
            del self.recent[:-64]
        if self.recent.endswith(SEP):
            self.reset_structures(self.end_pos(i))
            self.article_open = False
            self.title_start = i + 1
            self.title = self.title_raw = b""
            self.stats["article_title_openers"] += 1
            return
        if self.title_start is not None:
            if self.recent.endswith(TEND):
                b = i + 1 - len(TEND)
                value = self.span(self.title_start, b)
                if value is not None and 0 < len(value) <= 4096:
                    self.title_raw = value
                    self.title = self.text[self.title_start:b]
                    self.title_available = self.end_pos(i)
                    self.stats["titles_captured"] += 1
                self.title_start = None
                self.article_open = True
                self.in_tag = False
                self.tag.clear()
            elif i - self.title_start > 4096:
                self.stats["oversized_titles_skipped"] += 1
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
                if bytes(self.tag) == b"</page>":
                    self.reset_structures(self.end_pos(i))
                    self.article_open = False
                self.in_tag = False
                self.tag.clear()
            elif len(self.tag) > 512:
                self.stats["oversized_tags_skipped"] += 1
                self.in_tag = False
                self.tag.clear()
            return
        was_link = self.link is not None
        if not was_link:
            self.template_char(i, c)
        self.link_char(i, c)

    def run(self):
        i = 0
        while i < len(self.text):
            # A dictionary word expands into several decoded characters only
            # after all original bytes of that atom have been decoded.
            j = i + 1
            while (j < len(self.text) and self.starts[j] == self.starts[i]
                   and self.ends[j] == self.ends[i]):
                j += 1
            lo, hi = self.begin_pos(i), self.end_pos(i)
            self.scores.advance(lo)
            for k in range(i, j):
                self.char(k, self.text[k])
            self.scores.advance(hi)
            if (self.article_open and self.title_start is None and not self.in_tag
                    and self.title_raw and len(self.title_raw) <= 512
                    and word_byte(self.text[i])
                    and (i == 0 or not word_byte(self.text[i - 1]))):
                consumed = self.raw[lo:hi]
                # Gating uses an already-decoded COMPLETE WRT atom. No first
                # symbol cost is claimed. The continuation horizon is donor-known.
                if self.title_raw.startswith(consumed) and len(consumed) < len(self.title_raw):
                    suffix = self.title_raw[len(consumed):]
                    self.scores.begin("title_repeat", hi,
                        [Candidate(suffix, 1.0, self.title_available)],
                        (min(len(suffix) // 8, 7),), fixed_len=len(suffix))
                    self.stats["prefix_gated_title_repeat_starts"] += 1
            i = j
        self.scores.advance(len(self.raw))
        self.scores.eof()


def literal_wrt_byte(c):
    # Structural delimiters are not WRT control/high bytes and encode singly.
    assert c in (35, 93, 124, 125)
    return bytes([inverse_byte(c)])


def screen(raw, costs, dictionary, priors=DEFAULT_PRIORS, cap=2048,
           synchronize=True, event_output=None):
    costs = np.asarray(costs)
    if len(costs) != len(raw):
        raise ValueError(f"Cost count {len(costs)} != original WRT bytes {len(raw)}")
    if not np.isfinite(costs).all() or (costs < 0).any():
        raise ValueError("Cost file must contain finite, nonnegative bits/byte")
    if 0.0 not in priors or any(a < 0.0 or a > .9 for a in priors):
        raise ValueError("Priors must include 0 and lie in [0,0.9] (baseline >=10%)")
    sep = literal_wrt(SEP, dictionary)
    offset = raw.find(sep) if synchronize else 0
    if offset < 0:
        raise ValueError("No complete article separator in slice: cannot synchronize parser safely")
    decoded, starts, ends, _ = decode_wrt(raw[offset:], dictionary, skip_header=False)
    scores = Scores(raw, costs, priors, cap, event_output)
    parser = Parser(raw, decoded, starts, ends, offset, scores)
    parser.run()
    result = {
        "contract": {
            "input": "raw original WRT bytes; little-endian float32 bits/original byte",
            "scoring": "ideal whole-field likelihood mixture; no arithmetic framing or package costs",
            "candidate_selection": "decoded prefix only; source availability assertions enabled",
            "fallback_probability_minimum": .1,
            "combined_policy": "first causally active event; overlapping later events skipped",
            "warm_history": "cold parser/donor memory at first complete article separator",
            "truncated_fields": "unclosed slice-end fields excluded; cap-ended fields charged",
            "caveat": "independent branch savings overlap and must not be summed",
        },
        "raw_bytes": len(raw), "baseline_bits": float(scores.prefix_cost[-1]),
        "baseline_ideal_bytes": float(scores.prefix_cost[-1] / 8),
        "decoded_bytes": len(decoded), "unscored_prefix_bytes": offset,
        "parser_counts": dict(parser.stats), "screen_counts": dict(scores.stats),
        "schema_memory": {"keys": len(parser.memory.data),
                          "accounted_payload_bytes": parser.memory.bytes,
                          "payload_byte_cap": parser.memory.max_bytes,
                          "key_cap": parser.memory.max_keys,
                          "donors_per_key": parser.memory.donors,
                          "evictions": parser.memory.evictions},
        "scores": {name: scorer.result() for name, scorer in scores.scores.items()},
    }
    for row in result["scores"].values():
        neutral = next(r for r in row["fixed_priors"] if r["alpha"] == 0)
        assert abs(neutral["gain_bits"]) < 1e-9
        assert row["coded_bytes_covered"] <= len(raw)
    return result


def self_test():
    # Tests genuinely different matching/mismatching/selection conditions, not
    # an implementation-shaped equality alone. No fixture files are written.
    dictionary = {bytes([128 + i]): w for i, w in enumerate((b"page", b"title", b"alpha", b"beta"))}
    forward = {v: k for k, v in dictionary.items()}

    def encode_fixture(text):
        out = bytearray()
        pos = 0
        for m in re.finditer(rb"[A-Za-z]+", text):
            out.extend(text[pos:m.start()])
            w = m.group()
            if w[:1].isupper():
                assert w[1:].islower() or len(w) == 1
                out.append(64)
            w = w.lower()
            out.extend(forward.get(w, w))
            pos = m.end()
        out.extend(text[pos:])
        return bytes(inverse_byte(c) for c in out)

    text = (SEP + b"Alpha beta</title>\n<text>"
            b"[Alpha beta] [Alpha beta|Alpha beta] [Alpha beta|Other]\n"
            b"{infobox|country=Example|name=Alpha beta} "
            b"{infobox|country=Example|name=Wrong} "
            b"{infobox|country=Example|name=Alpha beta}\n"
            b"Alpha beta is repeated. Alpha wrong is not. </text></page>\n")
    raw = encode_fixture(text)
    decoded, _, _, _ = decode_wrt(raw, dictionary)
    assert decoded == text, (decoded, text)
    costs = np.full(len(raw), 5.0, np.float32)
    report = screen(raw, costs, dictionary)
    assert report["parser_counts"]["titles_captured"] == 1
    assert report["scores"]["title_selflink"]["matched_events"] >= 3
    assert report["scores"]["link_label"]["events"] == 2
    assert report["scores"]["link_label"]["matched_events"] == 1
    assert report["scores"]["schema_value"]["matched_events"] >= 2
    assert report["scores"]["title_repeat"]["matched_events"] >= 1
    assert report["scores"]["combined"]["coded_bytes_covered"] <= len(raw)
    # A mismatch has exactly the whole-field fallback penalty, independent of
    # the many baseline bits it covers.
    sc = Scores(b"abcdef", np.full(6, 7, np.float32), (0.0, .1), 20)
    ev = sc.begin("link_label", 0, [Candidate(b"xxxxxx", 1, 0)])
    sc.finish(ev, 6)
    assert abs(sc.scores["link_label"].fixed_gain[1] - math.log2(.9)) < 1e-12
    # Target-aware donors are rejected.
    try:
        sc.begin("link_label", 0, [Candidate(b"future", 1, 1)])
    except AssertionError:
        pass
    else:
        raise AssertionError("Future donor was accepted")
    # A cut variable field must not become a fake completed mismatch.
    sc2 = Scores(b"abc", np.ones(3, np.float32), (0.0, .1), 20)
    sc2.begin("link_label", 0, [Candidate(b"abc]", 1, 0)])
    sc2.advance(len(sc2.raw))
    sc2.eof()
    assert sc2.scores["link_label"].events == 0
    print(json.dumps({"self_test": "passed", "fixture": report}, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slice", dest="slice_path")
    ap.add_argument("--cost")
    ap.add_argument("--dictionary")
    ap.add_argument("--json", dest="json_path")
    ap.add_argument("--events-jsonl")
    ap.add_argument("--priors", default=",".join(str(x) for x in DEFAULT_PRIORS))
    ap.add_argument("--max-field-bytes", type=int, default=2048)
    ap.add_argument("--no-sync", action="store_true", help="Input begins on a proven WRT atom boundary")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.slice_path or not args.cost or not args.dictionary:
        ap.error("--slice, --cost and --dictionary are required unless --self-test")
    if args.max_field_bytes < 64:
        ap.error("--max-field-bytes must be at least 64")
    raw = Path(args.slice_path).read_bytes()
    costs = np.fromfile(args.cost, dtype="<f4")
    dictionary = load_dictionary(args.dictionary)
    priors = tuple(float(x) for x in args.priors.split(","))
    audit = open(args.events_jsonl, "w", encoding="utf-8") if args.events_jsonl else None
    try:
        result = screen(raw, costs, dictionary, priors, args.max_field_bytes,
                        not args.no_sync, audit)
    finally:
        if audit is not None:
            audit.close()
    result["inputs"] = {"slice": args.slice_path, "cost": args.cost,
                        "dictionary": args.dictionary}
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.json_path:
        Path(args.json_path).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
