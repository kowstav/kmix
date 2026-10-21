# Prefix-derived topic correction of an existing predictor

This is a proposal, not a measured compression result. The completed additive
unigram/topic screens were weak against the final coder; the fixed-pseudocount
V3 screen has not yet finished. Changing the prior's scaling alone does not
resolve the main conditional-model problem: an unconditional word distribution
can assign little probability to a word that syntax already predicts almost
perfectly. Mixing it into a strong conditional predictor may lose those bits.

## The statistical hypothesis

Let P0(w|c) denote a baseline distribution conditioned on the decoded context
c. Let Qz(w) be a prefix-derived topical distribution, and G(w) its global
reference. A useful hypothesis is that topical evidence modifies baseline
odds through a density ratio:

    P_tilt(w|c,z) = P0(w|c) [Qz(w)/G(w)]^lambda / Z(c,z,lambda),
    Z = sum_v P0(v|c) [Qz(v)/G(v)]^lambda.

The normalizer is mandatory. Scoring only the observed word's positive
log-ratio is an invalid free bonus. A complete word-level implementation
would require baseline probabilities on all alternative words; the existing
observed byte-cost traces do not contain them. An exact full-word normalizer
cannot be inferred from those traces or replaced by the observed target.

An inexpensive alternative defines a new normalized bit predictor at each
decoded prefix, using the already available final probability P0(1)=p.
Let A_b and B_b be causal topic and reference masses of the two next-bit
subtrees, including a common positive fallback. Define

    R_b = A_b/B_b,
    p_tilt(1) = p R_1^lambda / [p R_1^lambda + (1-p) R_0^lambda],
    logit(p_tilt) = logit(p) + lambda log[(A_1 B_0)/(A_0 B_1)].

This preserves the baseline at lambda=0. It is normalized for every prefix and
can be computed before the next bit is known. It deliberately defines a local
bit correction; because the baseline changes with each decoded bit, it is
generally NOT identical to the globally tilted word distribution above.
Do not advertise their likelihoods as interchangeable.

## Causal tree and fallback contract

Use the actual WRT dictionary tree, including overlapping two/three-byte
prefixes. The dictionary and its ranks already occur in the package. Aggregate
topic/global word mass on tree nodes; update learned counters only on ancestors
of completed decoded word leaves. A root may consult only the decoded parser
state, completed title/link facts and topic/global counts. It cannot consult
the upcoming word's class, spelling, length or difficulty.

For positive reference and topic subtree masses, construct auxiliary atom
distributions with a shared fallback, for example

    A = rho Q_topic + (1-rho) U,
    B = rho Q_global + (1-rho) U,
    0 <= rho < 1.

U must have explicitly defined positive mass on every legal atom-start byte
and continuation branch, including literals, case controls, escapes and
invalid dictionary continuations that the neutral coder permits. Merely
adding epsilon to the OBSERVED numerator is insufficient. A production
implementation must enumerate this same prefix support at encoder and
decoder. It may stop the topical correction after a literal/control leaf and
resume on the next parser-recognized root; the known triggering byte is still
charged under the distribution chosen before observing it.

At article and2^17 reset boundaries, specify whether topic counts persist and
which document state resets. Exponential decay uses completed dictionary
events, not future literal word boundaries. Starting a cut slice must wait
for a fully observed synchronization marker, as in the corrected V2 scorer.

## Finite comparison and evidence

Start with the existing fixed64 topic pseudocount model and global reference.
Keep a small fixed lambda grid, for example {0,1/4,1/2,1}. A Bayesian mixture
with initial neutral mass1/2 updates after each actual decoded bit. Its coding
likelihood pays for expert uncertainty; a prefix-derived fixed context may
partition posteriors only if its definition is priced and mirrored. A hindsight
choice of the best lambda at every bit is not compression. Charge all literal
and negative-ratio events, retain every candidate in the ledger and preserve
independent B/C/D confirmation before optimizing on A.

First obtain native FINAL bit probabilities for the compatible lexical
baseline and verify that their costs reconstruct the actual native byte-cost
trace. Neural-only probabilities are not that final baseline. A replay screen
can then evaluate the local correction on the identical decoded stream.
It remains a frozen-baseline screen: if native integration changes any shared
model/mixer updates, only the actual integrated archive establishes the gain.
Neither the completed additive screens nor V3 automatically test this tilt.

Require normalization and identity tests at roots, all dictionary depths,
literal/case/escape transitions, complete/incomplete markers, EOF and article
resets. Verify online counter sums and stable topic responsibilities. Finally
run separate native compression/decompression with byte/SHA agreement,
arithmetically quantized probabilities, complete duplicated code/model cost,
full warm RSS and independently calibrated single-core runtime.

## Resource objective

Ancestor updates are O(K times maximum code depth) per completed word, rather
than scans of44,515 words per bit. Document posterior changes require dotting
K-dimensional subtree vectors, so byte/bit gates and caching still matter.
Floating log/exp calls each bit can dominate runtime. A table or fixed-point
odds implementation needs a shared rounding/clipping contract and empirical
distortion accounting. Extra state competes with near-limit PPMD/NN RAM.

The candidate must save more payload than two copies of all added packed code
and metadata, while each submitted executable satisfies its own runtime and
memory limit. A tiny positive replay gain will not justify an expensive full
integration. At present no positive residual-tilt gain, resource measurement
or20% result exists.
