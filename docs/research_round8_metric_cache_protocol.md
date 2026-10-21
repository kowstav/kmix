# Geometry, bandwidth and costly-event retention: next cache experiment

Registered 6 October 2026 before results of these variants. The completed first
cache family mostly used negative correction strengths and did not pay its
parameters. This extension tests mechanisms that its finite family omitted.
Original C3 weights, decoder trajectory and all native hidden inputs are fixed.

Use the same native A/B128K for fitting. C/D are now exploratory previously seen
checks, not fresh confirmatory data. Register fresh G310M/H520M transformed offsets
(first128K each) before inspecting their contents. These lie in the old verified
586,459,020-byte transformed stream; production lexical preprocessing and warm
native history remain required later. If no A/B candidate beats its two stored
coefficient copies plus selector by at least64bytes, keep G/H candidate labels
unexamined and do not claim a useful cache. Their native baseline traces can be
generated and preserved for a later qualifying pilot.

Store two512-entry FIFO caches: all valid pairs and pairs whose completed native
byte cost exceeds2bits. The latter makes retention depend on earlier errors,
never on the current/future target. It is an admissible biased expert, not an
unbiased estimate of the corpus distribution. Matched target permutations
preserve the same selected target histogram, keys, ages and retrieval geometry.

For each past key dimension maintain Welford mean mu_j and variance v_j from
completed past prediction states. For raw geometry use mu=0,w=1; for centered
geometry use the prefix mean,w=1; for diagonal whitening use the prefix mean and
w=1/(v+1). Before16 keys use raw geometry for all modes. Evaluate both query and
all retained keys in the SAME current coordinate system, rather than centering
stored keys at different historical means. The metric diag(w) is positive
definite. Cosine and its normalization are computed in that metric. A zero norm
falls back to the prefix KT byte prior. Statistics themselves are decoder-built,
not a transmitted learned projection.

Enumerate17 fixed source families: the old raw K8,tau10,alpha0.5 control; raw K1
and K8,tau1000,alpha0.99; raw K8,tau100,alpha0.5; centered and whitened K1/K8 with
tau1000,alpha0.99; corresponding K1 same-cache permutations; costly-event centered
and whitened K1/K8 plus their K1 permutations. One-neighbor temperature has no
effect and is not counted as a separate hypothesis. Subtract max similarity in
every kernel exponential. Complete256-byte distributions have positive KT
smoothing, sum to one, and condition exactly on current bit prefixes using CDFs.

Fit generic [1,ell], each signed source [1,ell,f] with box[-1,1], and each
positive-recall source with theta_f in[0,1]. This distinguishes recall from an
anti-expert calibration. Fit a joint signed and a joint positive model using
the raw sharp K1, centered K1, whitened K1, hard-centered K1 and hard-whitened K1
features. There are37 fitted heads, plus identity; a six-bit selector is charged.
Coefficient copies and convex supporting-plane certificates match earlier
protocols. The certificate concerns ideal loss in this fixed family; Q16 cost
and its staircase tax are measured separately. Select by A/B priced Q16 gain;
never choose a setting from C/D or G/H outcomes.

Tests: original native trace/decode identity gates already passed, complete
kernel probability laws, metric self-similarity, raw equivalence before warmup,
current-coordinate centering, finite/positive variances, query-before-target,
costly-event retention timing, deterministic FIFO/permutations, and future raw
target/hidden noninterference. Independent finite-difference gradients, PSD
Hessian and supporting-plane bounds remain required. Source hashes, CPU/RSS,
parameters, negative strengths and all controls belong in the final report.

Production-selected full512 packed-key design is102,912bytes plus3,080bytes for
mean/variance/count and implementation control state. The two-cache instrumented
program and permutation tables are larger. None of those design figures is a
full10GB peak result. No training, rental or project deletion is performed.
