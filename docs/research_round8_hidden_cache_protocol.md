# Native hidden-state cache: registered deeper descendant

Registered 6 October 2026 before native hidden-cache results. This tests a
different mechanism from word-shape moments or a shipped semantic graph: the
unchanged C3 transformer already computes a context representation. Associate
that past representation with the byte actually decoded next, and retrieve
these associations from a bounded decoder-built cache.

The observation-only source patch exposes the existing final biased uint8
activation q5[192]; it changes no activation, probability or update. After each
completed byte, export a validity flag and those 192 bytes. A piece boundary or
out-of-vocabulary reset exports an invalid record. For byte i, query only record
i-1; the current byte becomes a cache target after all its eight predictions.
Initial queries and invalid keys use the identity/fallback. Data are cold native
A/B/C/D slices, so this is a diagnostic, not full warm-core qualification.

Before any fitting, require the rebuilt encoder's integer probability trace to
match the preserved native trace byte-for-byte, its actual archive to match an
independent unchanged encoder on A/B 32K, and independent raw decoding to recover
the input. Restore the original clang17 compiler through the official signed
LLVM repository; preserve all files and log tool installation. No weight training,
paid rental, existing-source overwrite or deletion is authorized by this test.

Each stored pair consists of a key known before the target, its norm, and a target
byte learned afterward. Search exact cosine neighbors in FIFO caches with 128
or 512 entries. Test full 192-dimensional and a fixed 32-dimensional signed-sum
projection, top eight neighbors, weights exp(10*(cosine-best_cosine)). Targets
produce a normalized 256-byte categorical distribution, smoothed with a prefix
KT byte prior. Condition this distribution on the already decoded current-byte
bit prefix. Never treat a whole-word likelihood along the realized path as a
counterfactual distribution.

Controls use the same cache's target histogram with a deterministic target
permutation, and ordinary recent-byte frequency with equal history. The neutral
bit probability must equal the original uint16 trace exactly. Export fixed
pre-observation signals and fit small bounded convex logit residuals on A/B only;
freeze them on C/D. Report generic calibration separately, coefficient cost twice,
all code/dictionary costs, RAM and CPU. A supporting-plane certificate concerns
the declared convex head, never optimal architecture or global compression.

Production cache RAM must be measured, not inferred from research trace files.
The full published C3 run leaves only 615,424 bytes below conservative decimal
10 GB. Its KV already uses KVI8, so the advertised 1.7 MB saving is unavailable.
Hidden-state traces are diagnostic outputs, not decoder side information.

Tests: record/byte alignment, invalid/reset handling, future-target
noninterference, query-before-update, full normalization and all bit-prefix
conditional probabilities, same-history permutation histogram, FIFO replacement
and duplicate-key tie ordering, projection determinism, exact native identity,
independent archive decode, float-gradient/Hessian and Q16 parity.

Extension registered before cache results: add a deterministic pseudorandom
Algorithm-R reservoir with 512 full keys and the same target-permutation control.
This spans much older prefix events than a 512-byte FIFO. Sampling uses a fixed
xorshift stream with modulo replacement; it is a reproducible pseudorandom
policy, not a claim of perfectly unbiased mathematical sampling. Invalid/zero
keys do not enter it. The joint head combines FIFO128, FIFO512, projection,
ordinary recency and the reservoir, with seven binary64 coefficients (56 bytes
per copy). Nine heads require a four-bit selector. This extension and its source
are registered before native cache fitting; the previous unexecuted five-signal
prototype is preserved separately. Research permutation tables and multiple
caches do not constitute production RAM measurements.

Final extension registered before any cache replay/fitting result: expose top
cosine for FIFO512 and reservoir512 and define c=clip((cosine-0.8)/0.2,0,1), with
c=0 for empty/invalid queries. Gated true and matched-permutation heads use
[1,ell,f,f*c]. A gated joint head adds FIFO and reservoir f*c to the original
joint features. This tests selective rejection rather than assuming a single
global cache strength is sufficient. Fourteen heads still use a four-bit
selector. Individual gated heads cost 32 bytes/copy; the gated joint has nine
coefficients, 72 bytes/copy. These are frozen statistical fits, not neural
retraining. The 0.8 threshold is a registered hypothesis, not an optimized or
universally valid similarity threshold. The original ungated arms remain
controls. This final source is replay_v3; results keep the existing queued
directory name hidden_cache_v2 to avoid a duplicate launch.

The representation mechanism is related to Khandelwal et al.'s frozen-model
nearest-neighbor language models, but here all memory is constructed causally
from decoded bytes and is bounded by the prize's memory budget. Its benefit on
other corpora is not evidence of a benefit for this compressor. [Original paper](https://arxiv.org/abs/1911.00172)

Advance only if frozen confirmation beats generic and matched controls with a
plausible package/CPU margin. Then integrate the residual into both native coder
directions, independently decode actual archives, obtain genuine warmed-core
controls and unused preregistered slices, and account for the complete package.
No 20% or record claim follows from this small diagnostic.
