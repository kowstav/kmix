# Higher-ceiling architecture search: expensive reasoning at lexical events

4 October 2026. Proposed experiments, not a measured gain or certified optimum.
This follows the new final-coder residual atlas and the negative frozen-model
screens. It complements research_round7_training.md, which specifies numerical
contracts, controls, sampling and the $70 spending gates.

## Why this branch has a different ceiling

The existing model spends its large recurrent/attention computation at each
post-WRT byte, including the second and third bytes of a dictionary code.
WRT has already turned a word into a short code, but the neural network still
learns relationships among those code bytes. A semantic word vector is not the
same object as the code prefix that happens to encode that word.

The record's byte model is highly trained. Our A/B temperature, exact-copy and
edit screens do not uncover a large easy correction. The new C/D atlas puts
37–40% of all final-coded bits in words seen previously in the slice but first
mentioned in the current article. Long-distance repeats within the article
hold only approximately9%. This points toward choosing words using reusable
relations between articles, rather than merely retaining old words longer.

The proposed change is to retain the ORIGINAL WRT stream and classical coder,
while moving expensive neural state updates to completed lexical events. A
small submodel handles code prefixes, punctuation, casing and novel spellings.
This is an interface/architecture change and requires training. It must not be
presented as a frozen-checkpoint improvement.

## Exact probabilistic interface

Let z be a completed dictionary atom, a completed literal word, or a precisely
defined syntax event. Let h_t summarize only completed events before the next
event. Let s contain the already observed bytes/control flags of the current
incomplete event. Define a normalized conditional byte distribution

    P_NN(b | decoded prefix) = D(b | h_t, s, u_t),

where u_t is a small byte-level state. Update h only at a causally recognized
completion; update u after EVERY original byte. The architecture never sees
the unknown word's spelling as input before it is decoded.

For a dictionary word w with a prefix code c(w), a normalized word model
induces the conditional probability for an already observed code prefix a:

    P(b | a,h) = sum_{w: c(w) begins a b} P(w|h)
                 / sum_{w: c(w) begins a} P(w|h).

The root must also include every literal/control/escape branch. These branches
have explicit probability mass; they are not free flags. The WRT tree is known
from the shipped dictionary. A byte-prefix head may instead parameterize this
tree directly, with each node's probabilities normalized. Then the product
along a complete word code is its probability. Heads may depend on the known
prefix and casing state, while the expensive h stays fixed within that code.

Do not materialize and softmax44515 full word logits every byte. Use the known
WRT hierarchy: its root and selected internal-node heads. Evaluate only heads
needed by the current decoded code prefix, plus literal/control alternatives.
The exact head dimensions follow dictionary.cpp, not an assumed256x256 code.

A small recurrent character/spelling head handles literal alphabetic runs.
It may condition on h, decoded prefix letters and the existing PPMD byte prior.
On termination, compose the observed spelling and update the lexical network.
Case-control bytes and code fragments need an explicit parser state; a mixed
case spelling can span several atoms. Any event definition used during training
must be the same prefix-recognizable definition used by the decoder.

The classical predictors consume every original byte/bit, unchanged. The byte
mixer receives the neural distribution at every byte boundary. If the new
neural distribution helps, cmix/SSE can use it; standalone word loss alone
does not establish a gain after the existing mixer.

## Representations without a huge stored word table

Use a small spelling composer plus a low-rank learned semantic code:

    e(w) = f_spelling(w) + U a_w.

f_spelling includes order-sensitive prefixes/suffixes and short character
n-grams, with optional bag-of-letter features as an ablation. It must retain
order: anagrams are rarely interchangeable meanings. a_w is an8- or16-dimensional
quantized vector for each dictionary word. Input and output use the same word
codes when tying improves the complete objective. Add a separately priced
word bias only if it pays after actual entropy packing.

For44515 words,16 dimensions of int8 codes occupy712240 uncompressed bytes
per copy, before entropy coding. Two copies cost1.424MB. Break-even from this
table alone is approximately0.01943 final bits/WRT byte, or0.08509 bits per
ASCII word using the measured133922554 occurrences. An8-dimensional version
halves the table cost. Count U, spelling parameters, scales, code and dictionary
changes as well. Compare int4/int8/codebook representations with measured loss
and the actual export container; do not infer packing from parameter count.

Because the table is fixed model data, its embeddings are available as possible
output candidates before the target is decoded. Feeding the TARGET embedding
into h before predicting that target is prohibited. Input embeddings enter
only after the word/atom is decoded. This distinction must be tested explicitly.

Spelling-derived output vectors can be materialized at decoder startup and
stored in RAM; materialization is not a free model database. Its code/weights
are supplied, all vectors are deterministically reconstructed, and the startup
CPU and total RSS are measured. Avoid storing a full float32 vocabulary matrix
in both the package and the decompressed model unless it improves total cost.

## Reallocate computation, while keeping weights small

The report measures586459020 WRT symbols and133922554 ASCII word occurrences.
The ratio is4.37909. That is an optimistic computation ceiling if an expensive
update occurs once per word and all other work is cheap. It is NOT a measured
speedup: dictionary fragments, markup words, literal spelling, syntax state,
output heads, PPMD and cmix still cost time. A prototype must count actual
causal update events and profile the full coder on realistic articles.

Let C_H be expensive-network work/update, C_D be byte-head work/byte, and
C_CM be unchanged classical work/byte. The approximate work is

    C_new = N_events C_H + T C_D + T C_CM + C_memory.

Compare against T(C_old_NN+C_CM) using measured cycle costs. A smaller N_events
can buy additional reasoning depth without additional stored parameters:

    h^(k+1) = h^k + F_theta(h^k, context),  k=0..K-1,

with shared theta and a small iteration embedding. Test K=1,2,4. All iterations
use the same known prefix; no target feedback enters between iterations. This
is deterministic repeated inference, not encoder-only best-of-K selection.
It pays CPU even when later iterations do not help, and training must support
the same K. Compare shared depth with an equal-parameter/equal-CPU ordinary
stack; extra computation is not automatically useful.

First establish K=1 parity and competitive loss. Then select K or an early-exit
rule using prefix-known confidence and a fixed budget. A future-informed rule
that chooses which iteration predicts the target best must encode its choice.

## Cross-article memory that can help first mentions

Build memory ONLY from articles already decoded. Maintain a bounded index of
title/alias keys, a compact article summary and a small collection of named
terms or explicitly parsed facts. Retrieve from a current title, completed
link target, or prefix-derived query. Each source record carries an availability
offset; assertions prohibit reading later articles, facts or model states.

An initial design uses32 rare/named terms per completed article, compact word
IDs/weights and a32-dimensional summary. At243425 articles,32 int32 term IDs
alone use31.158MB; summaries at int8 use7.790MB. Weights, keys, titles, collision
handling, indexes and replacement add memory. Cap the entire structure rather
than counting only these payload arrays. A100–128MiB budget is an initial
engineering target, contingent on actual baseline RSS below the10GB limit.

Retrieve a few documents at title/link boundaries, not a dense search at every
byte. Cache their shortlist while the current article/topic remains relevant.
For a query q, a cheap preliminary score can combine exact title/link matches,
summary similarity and overlap with already decoded rare terms. A learned
reader can attend to at most256–512 recalled terms or facts. The score and TTL
depend on decoded history, never future recurrence labels at inference.

For each memory item i, the selection objective is expected residual-bit gain
per byte of memory and per unit CPU, rather than recurrence frequency alone:

    value_i = E[future final-coder bits saved | decoded prefix]
              - storage_multiplier * memory_bytes_i
              - runtime_multiplier * query_work_i.

Training targets may use future outcomes; decoder features may not. Train and
evaluate the SAME prefix-only selector. The fact that99%of word occurrences
repeat does not make selecting the correct word free. Memory must distinguish
the desired entity/relationship among many plausible old terms.

Controls are essential: empty slots with identical capacity; real contents;
shuffled source/contents at the same storage/CPU budget; title/link-only
retrieval; summary-only retrieval; memory disabled in the same checkpoint.
This isolates semantic recall from extra scratch capacity, code changes and
more computation. Earlier memory experiments already showed why this matters.

## Training objective and $70 feasibility gates

Optimize the SUM of negative log probabilities for all original WRT bytes,
plus actual duplicated model description length. No loss per word averaged
uniformly across word types; no omitted spelling, literal, control or casing
cost. Select exported candidates with the native final coder.

    J = L_final(WRT stream | theta) + 2 L_export(theta) + L_code + L_other.

For early training, use byte-probability CE as a surrogate and lambda1 for
the basic model-rate term. If a rate surrogate is only an approximation to
L_export, measure its error and refit the export cost model. Pair all rate
arms with a matched lambda0 control. Preserve complete causal pieces and
token-length weighting, as specified in research_round7_training.md.

Do not spend the $70 on a full speculative architecture immediately. Before a
rental, implement a small correctness prototype that emits normalized205-byte
distributions, test every WRT control/prefix branch, and prove independent
round trips. Establish event counts, memory footprint and CPU throughput.
Then use the $4 pilot to quote delivered loss-bearing bytes/dollar for this
architecture, not the old model's tokens/second. A word event and a byte event
are different units.

The $12 stage compares: faithful original continuation; K=1 lexical model;
spelling-only versus low-rank word codes; and a small memory-content ablation.
Limit training according to measured useful tokens/dollar and actual storage
charges. Release the $36 winner budget only when learning curves show a path
to lower complete cost and the CPU implementation fits. Preserve the $8
export/evaluation allocation and $10 ancillary reserve. More budget buys more
experiments, not a guaranteed20% result.

## Decision criteria

1. Prefix causal normalization and byte alignment pass before any loss claim.
2. A small lexical prototype must beat or approach a faithful original model
   at matched parameter/computation budget. A weak freshly trained byte model
   is insufficient evidence against the current record.
3. Confirm useful capacity/compute scaling before increasing K, rank or memory.
4. Export and final-coder gain must pay all new model/code copies. A1.424MB
   semantic table must save more than1.424MB of final payload to break even.
5. A20% total result requires at most80339737 complete bytes against the
   official100424672 baseline. With unchanged fixed parts it requires about
   21.42% payload reduction. Larger side tables increase the required payload
   gain; lower NN perplexity is not this criterion.
6. Verify full enwik9 reconstruction, single-core runtime, RSS and disk use.

This is a bounded family with an explicit objective, not a proof that its best
configuration is the global optimum. Its promise is architectural: put more
useful computation at word/relationship decisions while paying fewer repeated
network updates and keeping the original stream available to the strong
classical predictors. Its actual gain remains to be measured.
