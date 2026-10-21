# Constructors, variables, constants and content-first grammar compression

5 October 2026. This proposal is a legitimate lossless-coding hypothesis.
The useful change is to factor the text into paid streams and exploit their
different statistics. It does not make high-frequency words, grammar or right
context free. No absolute optimum or 20% result has been established.

Current measured status: all three experiments are complete, comprising56
exact raw packet comparisons on four2M WRT slices. Every candidate increases
the matched-codec archive. The smallest skeleton penalty is+2.066% zlib9 /
+4.601% LZMA6 before additional decoder cost. The detailed measured section
below supersedes the historical launch descriptions. No job remains active.

## 1. What the proposed representation actually means

Let X be the exact source bytes. Choose a deterministic, reversible transform
F(X)=(C,G,A): C contains content anchors, G the constructor strings between
anchors, and A the required structure, separators, case, escapes and framing.
Nouns are one possible anchor rule; a fixed word list is a cheaper first probe.
Long words are not necessarily nouns, short words are not necessarily grammar,
and rare words are not inherently mathematical constants. Frequency and POS
classes are modeling choices with different accounting and decoder constraints.

A valid content-first decoder reads C, then the gap structure and G conditioned
on those already decoded anchors. Both the left and right anchor may be used.
For example, knowing `camel` before decoding a preceding gap is legal if its
content stream has already been decoded and paid for. This is a different
factorization from the present left-to-right WRT transformer.

Total package length, in bits, is

    L2 = L(program, weights, tables) + L(C) + L(A | C) + L(G | C,A).

The baseline is the actual qualifying package's complete length L0. We promote
a candidate only if L0-L2>0 with CPU/RAM constraints met. Original-order neural
costs cannot be reused for C after deleting grammar words: its contexts and
predictions have changed. Every escape, unseen template, order decision, code
table and last-byte/EOF convention also belongs in L2.

The information-theoretic identity is

    H(C,G,A) = H(C)+H(A|C)+H(G|C,A).

Changing the decoding order preserves the joint entropy of a reversible
representation. It can help a finite model approximate that distribution, or
exploit a memory/compute budget better. It cannot remove information merely by
renaming tokens. Expected modeling gains arise from reducing divergence from
the source distribution: E[L_Q]=H(P)+D_KL(P||Q), before package overhead.

## 2. Right context: a useful opportunity with a precise limitation

The exact value of a revealed right anchor R for a gap G, given left context H,
is I(G;R|H)=H(G|H)-H(G|H,R). This quantity can be positive. But if R was not
otherwise decoded, revealing it requires a paid channel and may cost more
because the content model no longer sees the preceding grammar.

For a consistent joint model, the simplest example makes the cancellation
explicit:

    P(R|H) = sum_g P(g,R|H)
    P(G|H,R) = P(G,R|H) / P(R|H)
    -log2 P(R|H) - log2 P(G|H,R) = -log2 P(G,R|H).

Thus exact marginalization of the SAME model does not improve its ideal joint
codelength by itself. A more suitable conditional gap model, content model,
template prior, or trained inductive bias is needed to obtain a better joint
distribution. Computing the sums for arbitrary neural gaps can also be costly.

`there _ a camel` concentrates probability but does not uniquely determine
`is` or `was`: `stood`, `appeared`, `comes`, `lay`, and other constructions can
be valid. A safe model gives alternatives nonzero probability and codes the
exact choice. Hard placement rules require a fully specified escape branch.
No POS tagger can recover tense, wording, punctuation and document spelling
without those decisions being represented somewhere.

An exact guess-and-repair pass is possible, but its repair channel must be
counted. Given a deterministic guess g(context), let e be the conditional
probability of an error and R the distribution of alternatives. Define

    Q(actual|context) = 1-e                 if actual=g(context)
                       e R(actual|context) otherwise.

The ideal expected cost is h2(e)+e H(R), where h2 is binary entropy, assuming
calibrated conditional probabilities. A model that guesses most slots correctly
can still lose on expensive mistakes, gap lengths, insertion positions and
model bytes. Guessing and repairing is one factorization of a normalized
probability model, not a separate entropy reduction. Blank locations and their
word counts must already be decoded or explicitly coded. This formulation
lets us test a rule-based pass rigorously rather than score only top1 accuracy.

## 3. Sets, multisets, subsets and word order

An ordered gap T=(t1,...,tk) determines its multiset M. M does not determine T.
If word w occurs n_w times, the number of distinct arrangements is

    N(M) = k! / product_w n_w!.

A uniform permutation code needs log2 N(M) ideal bits; fixed binary ranks need
ceil(log2 N(M)) bits. A contextual, nonuniform order code instead pays
-log2 Q(order | M,C,A). There is no universal requirement that every example
pays log2 N: a very predictable arrangement may cost much less. A complete
encoder still needs support for the other arrangements.

For `of the` and `the of`, the multiset is identical but there are two orders.
For three different constructors there are six orders, about2.585 uniform
bits. With repetitions, multiplicity must also be retained; an ordinary set
would confuse `of of and` with `of and`. These are different exact strings.

If a template contains m distinct entries and a gap chooses k of them, even
an unordered subset has binomial(m,k) possibilities. For uniform selection
the selector costs log2 binomial(m,k), plus L(k) if length is not otherwise
known. L(k) depends on the specified length model or integer code.
Allowing arbitrary order adds a permutation choice; allowing duplicates adds
a count/multiplicity description. A learned contextual model can compress
these choices, but cannot omit them. A template ID chosen using the target
gap must itself be encoded unless a decoder-known rule selects it uniquely.

The correct factorization is

    Q(T | C,A) = Q(M | C,A) Q(order | M,C,A).

For any true distribution, H(T|C,A)=H(M|C,A)+H(order|M,C,A). Dictionary-size
reduction alone is therefore not an archive saving. It can amortize shared
parameters, but the table, gap IDs, multiplicities and ordering remain paid.

For overlapping/subset templates, a normalized latent mixture is possible:

    Q(T|C,A) = sum_z Q(z|C,A) Q(T|z,C,A).

If multiple templates generate the same string, summing their probability is
valid when components are normalized. Transmitting a chosen z instead of
marginalizing adds a selector cost. A sophisticated architecture must account
for ambiguity rather than taking the cheapest untransmitted target-dependent
template. We should start with deterministic templates and explicit fallback.

## 4. Existing research and code, and what it establishes

The official [spaCy linguistic-feature documentation](https://spacy.io/usage/linguistic-features)
and [dependency-parser API](https://spacy.io/api/dependencyparser) describe
trained POS/dependency models and noun-chunk extraction. They identify
structure in supplied text; they are not exact grammar-word generators. A
parser run on the full original text at the encoder is not automatically
available to a decoder that has only decoded its content words. Either send
the necessary annotation, derive it from decoded data, or jointly code it.
Shipping a trained parser also incurs model/program bytes and CPU/RAM costs.

[Syntactically Informed Text Compression with Recurrent Neural Networks](https://arxiv.org/pdf/1608.02893)
uses character and SyntaxNet POS inputs in parallel recurrent layers. Its
[author code](https://github.com/david-r-cox/rnn-text-compress) is available.
The paper reports prediction accuracy and explicitly says document compression
benchmarks were not performed. Its reported accuracy change is not evidence
of an archive reduction, and full-text POS annotations need a causal/paid
decoder construction before use here. It provides an architecture hypothesis.

[Transformer Grammars](https://arxiv.org/html/2203.00633) and the
[authors' implementation](https://github.com/google-deepmind/transformer_grammars)
model joint tree/word actions with syntax-dependent attention masks. They
improve several sentence/syntax metrics, but their sentence-composition
bottleneck harms document perplexity and lexical copying. This argues for
retaining an independent lexical/retrieval memory rather than replacing all
long-range context with a grammar representation. The implementation is a
research model, not a Hutter-ready lossless CPU package.

[SEQUITUR's original paper](https://arxiv.org/abs/cs/9709102) learns repeated
ordered sequences as hierarchical grammar rules. This is closer to an exact
constructor-template dictionary than unordered bags. Its inferred compression
grammar is not the same object as a linguistic POS/dependency parse. The
reference website was inaccessible in this search; no code installation or
performance claim follows from that unavailable page.

Earlier local Wordle/any-order experiments in hutter_ideas_report.md increased
size in their tested settings. They do not prove all content-first syntax
models fail. A different conditional factorization needs its own matched
model, complete archive and runtime comparison.

## 5. Experiment I11: implemented and launched on Kaggle

Source: research_round7_constructor_split.py. Preregistration:
research_round7_constructor_preregistration.md. Launch5October14:00UTC,
PID1160, session355454655. No training, rental, deletion or Goal mutation.

The fixed lexicon has176 words. It is deliberately a cheap heuristic, not a
claim that those tokens always have a function-word POS in context. All other
ASCII words, including XML labels, become content anchors. The inverse WRT
mapping locates each word, but the transform moves original encoded raw byte
spans. Prefixes, case controls, separators, XML, binary and partial EOF tails
are retained byte for byte. The reconstruction does not depend on retagging
the content stream. Thus this screen covers the complete raw2M slice, not
only a conveniently selected English paragraph or decoded text fragment.

For each A/B/C/D2M slice, measure the same original WRT bytes against:

1. Direct gap words and separators, with a framed content stream.
2. A paid dictionary of ordered raw constructor tuples and gap IDs.
3. A paid dictionary of raw multisets, gap IDs and bit-packed order ranks.

Each uses two independently compressed channels with zlib level9 or LZMA
preset6. The packet includes channel lengths, headers, template table, IDs,
word lengths, multiplicities, separator lengths and final bit padding. All
six candidate packets must decompress and reconstruct the exact source.
The fixed lexicon is not needed by this packet decoder because raw word spans
are present; a future word-ID/learned grammar model would incur its own table.

The comparison baseline is the SAME codec on the SAME full raw slice. This
is a representation screen, not a comparison against the cmix/Hutter record.
Incremental decoder/program bytes are not credited as free: reported packet
gains are before that additional package cost. Negative packet results are
already negative before it. Constructor native bit budgets come from the
existing final-coder costs and disjoint raw spans; they do not simulate the
cost of reordered content under the current frozen transformer.

Preflight PASSED: 243 exhaustive length5 three-symbol permutation sequences;
duplicate/empty constructor lists; literal uppercase, binary, punctuation and
partial EOF fixtures; all modes and both codecs reconstruct exact bytes.
Every full-slice candidate also performs raw reconstruction and compression
roundtrip checks. Original input/cost hashes are included in each result.

All I11 comparisons are now complete and negative. I11b/I11c subsequently
tested simpler skeleton layouts; all are complete. Full measured results and
the current recovery state are in the measured handoff section below.

## 6. How to improve the representation without hiding costs

The pilot uses general varint framing rather than a specialized grammar code.
If it loses, examine losses from framed content, separator structure, unseen
templates and permutation ranks separately. A loss is not a proof that syntax
is useless. It identifies the cost of this exact implementation.

A simpler representation can preserve whitespace/markup in a skeleton with
explicit insertion positions, avoiding one length record for every word.
It must pay insertion flags/offsets and constructor lengths. I11b/I11c below
tested this change and retained a smaller, still negative penalty. Test a fixed
protocol on fresh slices, not a post-hoc best-of-six choice on the same data.
An adaptive prefix template dictionary can avoid a transmitted offline table,
but first uses and dictionary updates still have code costs, and the decoder
must perform identical admission/eviction/rescaling operations.

Use ordered templates as the default. Admit a macro only when repeated-use
code savings exceed its table/selector cost:

    gain(t) = sum_uses [L_fallback(t|context)-L_ID(t|context)]
              - L_definition(t) - L_admission/structure(t).

Partial templates can be a trie/DAG with shared ordered subphrases. Preserve
the original surface sequence through typed slots and an escape branch.
Choose template budgets and admission thresholds before validation. A tiny
template is only useful if it reduces the final coder's residual surprise;
frequent strings may already be nearly free under its neural/classical mix.

## 7. Subsequent architecture and training proposal

There are two distinct paths. The cheaper no-retraining path retains the
original WRT stream and adds a prefix-only constructor-run/valency expert to
the final native bit probabilities. It sees completed words and known parser
state, not upcoming words. Use soft class priors, article reset rules, bounded
template memory and a neutral expert. Normalize at each coded bit and round
identically in encoder/decoder. The actual uint16 traces now collected make
a controlled test possible; any winner still needs a native archive and
independent decode. This is I12, PLANNED, not already measured or running.

The content-first path is a new joint model:

    Q(C,A,G)=Q_C(C) Q_A(A|C) product_i Q_G(g_i | C,A,g_<i).

Give Q_G left/right content embeddings and completed previous gaps; a soft
grammar/ordered-template head and an explicit raw escape preserve arbitrary
syntax. Keep lexical copy/retrieval memory independent of the grammar head.
Use a compact shared vocabulary/backbone where possible. Share embeddings
only if their quantized serialized bytes are actually reused in the decoder.
Rare words remain exact literal or dictionary escapes; an offline rarity
classification/table cannot be a free source of information.

Train by minimizing TOTAL coded length, including C, A and G, with an explicit
model-byte penalty. Separate grammar accuracy is not the objective. For
example, if beta is the baseline constructor-bit share, r_G and r_C are
fractional reductions in constructor and remaining costs, and delta is
incremental package overhead divided by L0, then under matched accounting

    r_total = beta*r_G + (1-beta)*r_C - delta.

Use this as a scope budget, not as an exact counterfactual for reordered
streams. Constructor-only gains cannot exceed beta when all other costs
remain fixed and constructor costs cannot be negative. A20% total target
therefore requires enough constructor headroom or gains on content/structure.

Do not put the whole$70 into a new parser/transformer before representation
evidence. Follow the existing budgeted training plan: $4 compatibility and
throughput checks, $12 targeted pilot, $36 only for a surviving training
candidate, $8 quantization/export/CPU verification and $10 reserve. These are
spending caps, not quoted rental rates or purchased hours. Check live instance
prices/storage/network charges and supported GPU software before renting.
No paid compute has been started. Avoid allocating a second full embedding
table or another large parser unless expected code savings exceed their size.

For a paid pilot: fix two paths' parameter-byte/compute caps; train matched
models or small adapters on development data; quantize/export as the decoder
will use them; evaluate new held-out slices AND the full archive objective;
freeze the selected hyperparameters; measure per-stage CPU and peak RAM;
then independent byte-for-byte decompression under prize restrictions.
The existing GPU/native fidelity failure must be repaired before using GPU
loss numbers to rank final-coder candidates. A20% neural-only change does not
by itself demonstrate20% package reduction.

## 8. Handoff and recovery

Remote result directory:
/kaggle/working/hp_round7/constructor_split_v1; exclusive launcher and log:
research_round7_launch_constructor_split.py, constructor_split_v1_controller.log.
Inspect research_round7_constructor_status.py; do not duplicate the process or
overwrite its existing directory after an error. Preserve manifest, per-slice
JSONs, summary, controller log, source and matching hashes locally.

Larger native final-bit trace collector PID1097 is a separate existing job;
reuse it. C/D32MB traces and original2M inputs are local with verified SHA256:
C trace dd0a0060fcc425f9c23613f2695ab8a3162dae31d4ba25339e0b1e58dbfb39ff;
D trace 4b2300205bfb21664f02f74f329083560e24bfb7b2e3cac7954fba0490597f1f.
All four A/B/C/D traces are now complete, local and validated against the
old archives/costs. Trace completion is a measurement prerequisite, not a gain.

Managed Goal remains usageLimited as last inspected; no Goal was resumed or
changed. New work here is the directly authorized human continuation. A
heartbeat must continue to respect its limits rather than auto-resume it.
Every experiment in this document has zero project deletions and zero paid
rental spending. Models and source data are preserved.


## Measured constructor results and current handoff,5October2026

Updated 2026-10-05T14:23:29.109612+00:00. I11/I11b/I11c all COMPLETE; no constructor or native trace
process remains active. The three experiments made56 matched-codec packet
comparisons over four2M original WRT slices. All56 exact raw reconstructions
and compressor roundtrips PASS; every candidate is larger on every slice.
The following aggregate compares each fixed representation with its own
matched original-source codec. These are not cmix/Hutter record deltas.

| Representation | zlib9 increase | LZMA6 increase |
|---|---:|---:|
| Framed gaps: direct | +21.623% | +20.415% |
| Framed gaps: ordered_templates | +18.847% | +21.493% |
| Framed gaps: multiset_plus_order | +19.473% | +22.204% |
| Two-byte marker: direct | +6.121% | +7.882% |
| Two-byte marker: constructor_word_table | +3.559% | +5.788% |
| One-byte marker: direct | +4.628% | +6.695% |
| One-byte marker: constructor_word_table | +2.066% | +4.601% |


The one-byte-marker paid word-table variant is the least costly skeleton:
zlib original3,623,465B vs candidate3,698,340B (+74,875B,2.066%);
LZMA original2,894,828B vs candidate3,028,020B (+133,192B,4.601%).
Incremental decoder/program cost is excluded from these packet differences,
so adding it cannot rescue these already negative results. Per-slice values,
source/dependency/input/cost hashes and timing are in the preserved JSONs.

The fixed176-word lexicon matches629,700 of1,884,022 ASCII word events
(including markup), but its disjoint original word/case spans carry17.200%
of the sampled native ideal bits. The per-slice shares are7.922/18.083/
17.777/19.690%. This is an accounting result for this heuristic and these
slices, not a universal function-word inventory or whole-corpus bound.
With every other cost fixed, even zero-cost encoding of just these selected
spans cannot deliver20% on this sample. A20% overall target needs gains on
content/structure too, or a different broader scope with measured headroom.

87.345% of1,254,326 constructor gaps have length zero or one, offering no
permutation sharing. Merging ordered case-folded tuples into multisets reduces
distinct template counts by only2.883–6.167% within the four slices. The
observational H(order|multiset) total is11,573.927bits. This is a fitted
descriptive statistic, not an untransmitted probability table or achieved
code length. The pilot's exact raw multiset code pays order ranks; a better
contextual order model could reduce their cost. It does not remove the paid
content stream, slot/escape information or lost cross-channel correlations.

I11 consumed175.321 prototype CPU seconds and176.164 wall seconds; I11b
45.423/45.432 and I11c40.640/40.649s. Reported process peak RSS is593,568/
593,696/593,952KiB. These are Python experiment/runtime peaks and include
process setup/inheritance; they are not measured standalone C++ decoder
requirements, full-corpus runtime, or a qualifying CPU package. No new
parser/weights, neural training, rental, deletion or Goal mutation occurred.

The native final-bit collector also completed all four2M slices with PASS.
All128MB of uint16 traces and8MB original inputs are local; all source input,
trace and preserved native archive hashes match. Independent local blockwise
reconstruction validates64M actual coded-bit probabilities in[1,65535] and
maximum byte-cost error below9.54e-7bits (fixed gate1e-4). Native archives and
EVERY prior float32 byte cost are identical to the preserved baselines.
Individual native user CPU is1236.291/1312.900/1292.865/1313.031s for A/B/C/D;
peak RSS max6,043,696KiB. This proves measurement identity, not new compression.
Local evidence: research_round7_finalbit_local_validation.json and
research_round7_lex_finalbit_2m_v1_{manifest,results}.json.

### Next steps and stopping gates for this hypothesis

Do not repeat the losing static layouts or spend$70 merely to reproduce their
generic-codec screens. A still valid hypothesis is a compact CONDITIONAL gap
model exploiting paid decoded left/right content and a better content model.
It needs a new joint distribution Q_C(C)Q_A(A|C)Q_G(G|C,A) and total-length
evaluation, not the old transformer's scores applied to reordered bytes.
The controlled no-retraining alternative is a prefix-only syntax/template
residual on the original final-bit coder, with normalized integer probabilities.

I12 prefix-only constructor-run expert remains PLANNED, not running. It should
use completed ASCII words (including literal I/i), a fixed constructor lexicon,
bounded ordered run/trie state, left content class/ID and punctuation/markup
state. Commit a word only when the decoded separator establishes its boundary;
never choose an expert from the target's future word/length/POS. Maintain a
neutral expert and a global non-constructor fallback; preserve nonzero support.
Build the expert's full word-trie branch probabilities and compare its binary
log-odds to its global-prior expert, then apply a clipped signed residual to
the actual native uint16 p. Quantize every candidate and mixture. Do not add
independent word gains or use a target-dependent activation mask. Test neutral
byte-for-byte identity, all escape/case/EOF bits, sparse memory rescaling and
reset semantics first. Preregister state/row caps and scales; screen A/B32K,
then larger regions ONLY if a priced signal survives. Freeze on development
and confirm on new E/F regions; these A/B/C/D are already examined research
data. A positive screen still needs a native archive, independent decode,
full package bytes and CPU/RAM verification.

Existing pending I04b retrieval/I06 syntax-source-surprise/I07 memory controls/
I08 phonetics/I09 hazards/I10 trained shared residual/P01–P05 retain their
own registered gates. Prioritize high-cost content/first-mention residuals
alongside grammar, given the measured constructor budget. The staged$70
training plan remains unchanged, with no spending or promised rental rates.

### Exact recovery commands and evidence

Use the newest user-supplied session credential only via HP_KAGGLE_BASE, and
the existing kaggle_research_client.mjs bridge. Kernel currently
788f499d-4818-4c63-974e-bc26b298ddf0, session355454655. Read-only status RPC:
research_round7_constructor_all_active_status.py for I11/I11b/native trace;
research_round7_constructor_skeleton_v2_status.py for I11c. All are complete;
no launcher should be run again against its existing exclusive directory.

Directories/logs: constructor_split_v1 / constructor_split_v1_controller.log;
constructor_skeleton_v1 / constructor_skeleton_v1_controller.log;
constructor_skeleton_v2 / constructor_skeleton_v2_controller.log;
lex_finalbit_2m_v1 / lex_finalbit_2m_v1_controller.log, all below hp_round7.
Preserved compact outputs are locally prefixed research_round7_ plus the
corresponding directory/log names. Sources, launches and preregistrations are
also local. I11c source was generated by checked anchor replacements without
editing the measured I11b source. No deletion was needed; persistent free
space at the final existing-job check exceeded8.7GB.

Local reproduction/validation with the bundled Python:

    python research_round7_constructor_assess.py
    python research_round7_constructor_skeleton_assess.py v1
    python research_round7_constructor_skeleton_assess.py v2
    python research_round7_finalbit_local_validate.py

The first constructor assessment has now verified all four local original
inputs, costs, source and result equality. The final-bit validator independently
checks probability alignment/reconstruction and hashes. Constructor source
scripts use Linux resource accounting; run full original experiments on Kaggle
or Linux rather than silently deleting that instrumentation on Windows.
Managed Goal remains usageLimited; no automated continuation may bypass it.
Latest user-directed continuation performed this work, without resuming it.
No20% gain, absolute optimum or qualifying archive breakthrough is claimed.
