## Later native measurements and engineered descendants

The final combined-CM comparison is complete. Every entry below is an actually
written native archive with independent decoding and identical encoder/decoder
neural probability trajectories. Values are payload-byte savings versus the same
native teacher on the same 64KiB slice, before model/package cost.

| Model | A | B | E | Initially sorted packed-model growth per copy |
|---|---:|---:|---:|---:|
| Unweighted finetune | 105 | 14 | 20 | 85,922B |
| Cut107, half rare loss | 105 | 18 | 19 | 85,940B |
| Cut1392, zero rare loss | -106 | -118 | -139 | 85,927B |

A overlaps core training. B/E were held out from those fits but seen elsewhere.
Cold 64KiB tests do not justify full-corpus extrapolation. Native decode CPU and
RSS are recorded per candidate in research_round9_core_native_codec_v3_results.json.
The initial model prices use sorted observer tensor order. A separate packing job
recovers the original container order to distinguish repacking overhead from
changed-weight cost; native tensor identity is mandatory before archive reuse.

Direct dictionary-word warm-start followed by full-bit mixture training is complete.
The frozen random-basis seed7106 loses 9.63545B on E and 15.14074B on F, total
24.77620B relative to the stronger adaptive source reference. Spelling seed7107
loses 9.35914B and 15.53255B, total 24.89170B. Better dictionary-only CE did not
produce better full-bit compression. That is a finite negative experiment, not
a rejection of all word models or proof of an optimum.

The unchanged selected-core E/F raw baseline is 1.5019641266 bits/symbol for
190,084 targets: common/unlabelled 1.3821668982, rare 2.3632757110. Compare each
distributed finetune against a zero-update baseline with identical input mode,
targets, resets and contexts. Redacted-symbol losses need their paid literal side
stream before they can be interpreted as original-text compression.

research_round9_core_selective_worker.py tests six arms times seeds7006/7007,
rungs128/384, on the same A/B sampled article prefixes as distributed_core_v2:
unembedding-only (39,360 scalars), recurrent-gates-only (449,307), last-block-only
at learning rate1e-4; all-core3e-5 paired control; the same control plus .01
code-cell penalty; and half rare loss plus that penalty. Every frozen parameter
must remain byte-identical at each rung. For each quantized tensor with minimum
native code-level spacing s and initial w0, the penalty is

    R = mean_tensors mean_elements max(|w-w0|/s - .49, 0)^2.
    J = weighted_full_cross_entropy + .01 R.

This smooth penalty discourages code-index flips. It is not an actual entropy or
compressed-size estimator. Evaluate full C/D and E/F original-symbol losses,
export promising candidates through the native reader, then price packed model
and actual combined-CM archives. Native/GPU arithmetic parity remains unresolved.

research_round9_word_cache.cpp and its worker implement eight no-retraining
completed-word donor probability laws. Keep the last256 completed words, their
actually observed encoded spelling (1..64B), letter bags, and preceding constructor
class. A donor becomes available only after its delimiter completes. Query the
longest matching proper encoded-word prefix among the last8 decoded bytes.
Next-byte donor counts plus .001 Dirichlet smoothing over256 bytes are normalized
within the already known current-bit prefix, then quantized to Q16.

The eight laws are counts, recency8/64/256 words, preceding constructor class,
letter-bag cosine to the fourth power, first-letter equality, and a joint
constructor/letter-bag/last-letter law. Fit one scalar convex mixture coefficient
per law on A/B, select on C/D with identity available, freeze before E/F.
Nonzero future-prefix mutation and exact zero-mixture identity are required.
These are direct output laws rather than hidden-feature proxies. Production
semantic parsing, native independent decoding, model/code/memory pricing and
full warm evaluation remain required. They do not assert an intrinsic semantic
connection merely because two words share letters.
