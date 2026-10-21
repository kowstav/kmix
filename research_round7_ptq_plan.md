# A finite post-training rate–distortion search

5 October2026 IST. This is a bounded experiment, not a promised breakthrough.
No SGD or neural learning run has started. The three current candidates change
selected existing Q4 values while retaining scales, float parameters, shapes,
RoPE and the native architecture. This distinguishes lossy *model* changes
from lossless compression of the original dataset: the new encoder and decoder
must use the same changed predictor and still reconstruct all input bytes.

The exact tensor-aware codec already saves54862B across the two BF16-model
copies after matched lab loader overhead. Further model storage gains are
useful only when they exceed the final-coder penalty. With N=586459020 symbols,
5,868,864 Q4 values and two stored weight copies, reducing entropy by0.1 bit per
weight saves146721.6B and permits only0.0020014 bits/symbol of additional
final-coder loss. A smaller weight file alone is not a better compressor.

The native pilot uses the original BF16 candidate as a fixed baseline and
three explicitly frozen transformations:

1. Zero q=±1 only in MLP down projections.
2. Zero q=±1 in both MLP projections.
3. Zero q=±1,±2 throughout Q4 tensors as a deliberately more aggressive bound.

The third candidate may damage predictions severely. Its role is to measure
the rate–distortion frontier, not to assert that small coefficients are
unimportant. Each export verifies all434 decoded tensor byte arrays against
the intended candidate. Original models are preserved. The shipped tensor
order is preserved so RoPE tables remain eligible for exact reconstruction.

Two matched32768-symbol cold-prefix native tests compare actual final-coder
likelihood and archive bytes, using the same executable, vocabulary, original
input and classic-model initialization. They do not replay GPU predictions.
At most two native jobs run concurrently. The model-storage saving is counted
twice; a hypothetical full-stream extrapolation is explicitly marked
unvalidated. A tiny cold pilot cannot qualify a record or establish a full
warm-stream gain.

If coarse zeroing fails, do not run a huge blind threshold sweep. A better
possible search is activation/Fisher-weighted post-training quantization. For
an observed linear layer y=Wx and a local output-distance proxy,

    Delta D approximately sum_i h_i (w_i - s g(q_i))^2,

where h is estimated from a fixed causal calibration stream and includes
input activation scale. A rate-aware discrete assignment can minimize

    q_i = argmin_q [ h_i(w_i-s g(q))^2 + lambda*(-log2 r_layer(q)) ].

The symbols remain within the native Q4 range, avoiding an unrelated decoder
architecture change. Tensor histogram/framing bytes and scales must be priced.
The proxy is not the real final-coder objective; only exported native results
select a winner. A local softmax approximation gives

    KL_bits(P_original || P_changed)
      approximately Delta z' [diag(p)-p p'] Delta z / (2 ln2).

This explains why small raw coefficients may still have a large predictive
cost, and why quantizing all low-magnitude values uniformly is unreliable.
If optimizing assignments uses target-driven parameter fitting, label it as
calibrated post-training optimization; do not conceal it as a lossless codec.

The preserved sparse PPMD training priors and full token file are absent in the
new session. Any GPU calibration or training must explicitly regenerate its
priors/pieces and reproduce the native baseline. Supplying uniform priors or
the transformer's final output probabilities instead is a different model
contract. Never compare that loss directly with the old full-context baseline.

Advance a candidate to independent C/D and longer article pieces only if the
storage-minus-payload tradeoff is positive on meaningful pilots. Then export
the actual production package, measure single-core CPU/RSS/disk, and run full
compression/decompression. The subsequent$70 training plan remains separate;
post-training storage experiments do not authorize extra rental spending.
