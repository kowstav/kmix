# Reproduced lexical checkpoint: residual costs and test priorities

Measured5October2026. These are four original-order enwik9 WRT slices,
2,000,000 symbols each, with the actual lexth11c C3 checkpoint and matching
inference macros. Neural and classical histories start cold. Independent
full-slice decodes are being recovered after a session restart; all four
compression runs passed exact32K prefix-cost checks. This is not a qualifying
full archive or a matched production comparison against the earlier warm-neural
reference. The executable/checkpoint hashes are in the recovery manifest.

| Slice | Native archive bytes | Ideal bytes | User CPU seconds | Peak RSS KiB |
|---|---:|---:|---:|---:|
| A |187401|187363.087|1091.92|6042088|
| B |437079|437041.141|1146.46|6043580|
| C |447061|447023.932|1190.98|6043072|
| D |439381|439343.313|1195.96|6041512|

Cost traces are exact outputs of the final native coder, not standalone neural
loss. Attribution uses the inverse WRT byte map and includes case controls in
their word spans. Truncated slice prefixes before a complete page separator are
excluded from word attribution; their bits remain in the total denominator.
The assigned-word union reproduces the attributed bit sum within1e-4bits.

| Fraction of all final-coded bits | A | B | C | D |
|---|---:|---:|---:|---:|
| ASCII word spans |77.258%|82.198%|82.028%|85.295%|
| Seen earlier in the slice, first in current article |43.237%|38.688%|36.845%|38.937%|
| Literal spelling word spans |21.602%|9.142%|9.288%|11.046%|
| Distinct anagram donor earlier in this diagnosed slice |4.463%|6.053%|7.051%|8.941%|
| Distinct anagram donor earlier in current article |0.080%|0.417%|0.426%|0.649%|

The classifications overlap. ASCII words include XML tag words and literal
fragments; a word first in a2M slice is not globally new in enwik9. The
anagram donor has at least four letters, at most32, and is a distinct
case-folded word with exactly the same letter multiset. Prefix/suffix tests use
four equal letters and exclude an identical word. Every donor precedes its
diagnosed target; no later occurrence is counted as an available hint.

The community's anagram proposal is therefore testable but has a limited
ceiling in these cold-history samples. A mechanism which only improves the
marked same-article anagram spans cannot save more than their0.080–0.649%
baseline bit budget, even if it codes those spans for zero bits and incurs no
overhead. The corresponding slice-memory family has a4.463–8.941% ceiling on
these slices. Neither is a bound on a full warmed corpus, different spelling
relations, or a model whose hints change predictions elsewhere.

An anagram relation also leaves order to encode. Given a multiset ofm letters
with countsn_j, its unconstrained order entropy is

    log2(m! / product_j n_j!).

A restricted dictionary may reduce that to the entropy over compatible words,
but identifying the donor, selecting the relation and paying any exception
still matter. Renaming dictionary codes cannot remove word-choice entropy.
Common prefixes/suffixes cover much more residual cost, but they identify
large ambiguous groups. Count that ambiguity rather than assuming the donor
determines the target.

Repeated hard words differ by domain: A includesbonaventura,pocahontas,uesugi,
rheims; B includesuunet,anycast,routable,relaying; C includesalexanderson,
optimised,radiotelephone,excursion; D includesgroundskeeper,derisive,
eavesdropping,dithyramb. Rank candidates both by total paid bits and by bits per
occurrence. A rare70-bit name is not automatically a better global target than
a common8-bit word repeated many thousands of times. The complete per-word
costs and contexts are in the four local lex residual-atlas JSONs.

The highest-budget category remains first mentions within articles of words
already seen elsewhere. A topic-only unigram family already failed after
charging its selectors and tables. The next learned mechanism should combine
title/body state, syntax, spelling and a bounded memory of completed lexical
events. It must predict the whole choice, including literal/syntax fallback,
rather than activate after an unknown target's class is revealed.

As a conditional planning calculation, if these class shares held across the
whole payload and fixed components remained unchanged, a21.42% payload
reduction confined to this category would require recovering approximately
49.5–58.1% of its current bits. This is an ambitious requirement, not a
forecast. A new head should therefore demonstrate substantial paired
final-coder savings before committing the$36 winner-training allocation.

The existing T4-compatible FP32/SDPA evaluation harness is preserved, but its
FLA/typing dependencies are absent in the new session. The current runtime is
Python3.12.13, Torch2.10.0+cu128, Triton3.6.0, while the archived project
declaration specifies Python3.11 and Torch2.12. Do not upgrade the entire stack
blindly or assume compatibility. The T4 has compute capability7.5 and lacks
native BF16 support; BF16 scale rounding is still part of the checkpoint
contract. A small isolated dependency/parity pilot must precede any training.
No uniform or neural-output substitute may replace missing PPMD priors.

All original models, inputs, results and failure logs were retained. C/D native
archives and four8MB cost traces were saved locally. A/B archives were lost
with the old ephemeral filesystem and are being regenerated against preserved
costs. No cleanup deletion or paid rental occurred in this continuation.
The later isolated fla-core/typing installation imports successfully without
upgrading Torch. All three structural loads pass; a true-prior/native-GPU
logits pilot is queued after native recovery. C/D complete independent2M
decodes have passed original SHA256 and length; A/B regeneration/decode remain
in progress. Neither structural loading nor these round trips establishes a
compression gain.
