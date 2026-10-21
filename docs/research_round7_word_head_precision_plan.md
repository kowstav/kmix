# Exact word probabilities, rate and CPU engineering

This refines the word-event architecture proposal; no implementation or
training result is asserted. Keep the initial WRT/classical stream unchanged.
The new word model must include literal/spelling, syntax and case fallback,
with its gate determined before the unknown outcome. A cheaper large state
updates on completed lexical events while a smaller byte state observes every
decoded byte. Literal word completion is known only after its terminating
byte, so its update cannot be moved earlier using a future delimiter.

The133.9million ASCII-word count and586459020 WRT symbols give approximately
4.379WRT symbols per word. The20.084935MB official-target saving requires
approximately1.20bits per word if all savings came from word spans. A new
44515x16int8 learned residual embedding costs712240bytes per copy and thus
approximately.0851more bits per word across both copies. This branch must
therefore seek roughly1.28bits per word in payload benefit before other added
code/rate costs. These are planning conversions using full-corpus counts;
they do not assume a measured word-head improvement.

Two normalized alternatives deserve a matched pilot:

1. **A head on the actual WRT word tree.** Predict every next branch, then
   multiply probabilities on the observed leaf path. Charge dictionary versus
   literal/syntax/case choice at the root. The largest dictionary-only path
   has128 first-byte choices,112 second-byte choices and80 third-byte choices:
   at most320 child scores per word. A16-dimensional head requires at most
  5120 scalar multiply-accumulates for those scores, plus normalization.
   It is cheap, but its arbitrary frequency-code groupings may restrict useful
   semantic comparisons. Global word embeddings do not automatically provide
   a child's aggregate mass by averaging its descendants' embeddings.
2. **An exact global low-rank head.** With queryh and word keye_w of dimension16,

       Q(w|h) = exp(h dot e_w + b_w) / sum_v exp(h dot e_v + b_v).

   All44515keys need712240 scalar multiply-accumulates and44515 exponential
   evaluations per query. For133.9million events, that is approximately95.4
   trillion multiply-accumulates and5.96trillion exponentials. These operation
   counts are not timing measurements. Cache dictionary-derived spelling keys
   once per model/load; add any learned per-word residual/bias to the package
   accounting. A712240-byte int8 key table can fit in a CPU cache, but its
   actual cache behavior beside NN/PPMD state must be benchmarked.

The full head is not automatically too slow: update it once per word and
reuse its distribution throughout that word code. Conversely, scalar standard
library exponentials could consume the runtime budget even if dot products
are fast. Benchmark exact complete prediction, tree-mass creation and memory
traffic together; a matrix-multiply-only timing is insufficient.

Existing WRT dictionary ranks form contiguous intervals for second/third-byte
groups. A cached prefix sum of word masses permits subtree mass queries.
First-byte values240..255 combine a two-byte interval with a three-byte
interval; include both. The second byte distinguishes them. Do not assume
first>=240 alone identifies a three-byte word. Given a decoded word prefixs,

    P(next byte=c | s,h) = mass(words beginning sc) / mass(words beginning s).

The byte/word hybrid uses these conditional masses and an explicitly
normalized fallback distribution. Invalid or unsupported code paths retain
fallback mass. A word distribution over valid leaves alone cannot silently
replace the full byte distribution.

Do not apply the existing byte-level1e-6 floor independently to every word:
44515 such floors would reserve.044515probability mass. Word-mass flooring,
fallback support and final bit-CDF quantization are distinct operations and
must be defined together. A masked top-k vocabulary also needs an escape
distribution with a paid normalized residual; its unknown target cannot
select the mask.

A deterministic candidate softmax implementation can quantize logits in
base2 to a1/256grid, subtract the maximum, and compute integer masses through
a256-entry fractional exp2 table plus integer shifts. With Q32 table scale,
each mass is at most2^32 and the sum over44515words is below2^48, fitting
uint64. Very small masses may be zero; the byte fallback maintains complete
support. Preserve the exact table, rounding rule, saturation and shifts in
both directions. Quantization-aware training must use this forward definition;
a float softmax followed by a different CPU approximation is not export parity.
This is a design candidate, not evidence that its distortion is acceptable.

Integer key/query dot products can also improve reproducibility. A16-way sum
of signed int8 products fits int32. Row/column scales, biases, query
quantization and clipping still require an explicit arithmetic contract;
exact integer accumulation alone does not make a floating core portable.
Check complete coded probabilities/archives on AVX2 and runtime-dispatched
AVX512 paths and independent CPUs before accepting a submission.

Training the full head must not allocate a65536x44515float32 logit tensor
(approximately11.67GB) plus a similarly sized gradient. Compute exact
log-sum-exp by vocabulary tiles and recompute tiles for backward, accumulating
query/key gradients. A32768x4096float32 tile is512MiB; measure the full
activation/optimizer peak before selecting micro-batches. Sampled softmax can
be a training approximation, but cannot substitute for the normalized full
distribution in coded likelihoods or winner selection.

Compare the two heads on the same complete legal pieces, true PPMD priors,
token/word weighting, code/rate budget and core initialization. A word-event
state change cannot reuse unchanged byte-state weights as if their temporal
semantics were preserved. Adjust/init the KDA time-scale as a hypothesis and
retrain/fine-tune under the explicit control protocol. Word labels, casing,
dictionary code and OOV delimiter timing must match the native parser exactly.
The$70plan should fund a small paired pilot before choosing the main arm.
