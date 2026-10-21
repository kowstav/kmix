# Round 13: four-core CPU execution and audit repairs

7 October 2026, initial checkpoint 13:48 UTC. This report records finite measured
results and actual jobs. Theory is in research_round13_theory.md; the detailed
handoff is in research_round13_pre_experiment_report.md. All 96 ideas are not
thoroughly tested, and their absolute best descendants are not established.

## Actual core use and completed representative cases

The constructor notebook completed 144 exact paid archive/inverse cases on
sixteen disjoint 1 MiB raw-corpus regions. Four persistent workers used CPU IDs
0,1,2,3. Its measured worker CPU was 1,669.667 s in 433.334 wall-seconds:
3.853 cores on average, about 96.3% of the four-core capacity. This directly
addresses the cancelled single-core notebooks; it is measured execution, not an
OMP setting presented as parallelism. Kaggle's four logical CPUs need not be
four physical cores, so no fourfold speedup is promised.

Nine arms were fixed in advance: unigram, Markov, two strengths each of paid
right/coarse-wrong/left anchors, and paid bags. Select on even-numbered regions;
freeze the winner before opening odd confirmation outcomes. The selected
coarse-right alpha=4 arm used 3,014,495 B on the eight development regions versus
3,018,441 B for Markov, a 3,946 B within-factorization saving. On the eight
confirmation regions it lost 240,471 B against their complete gzip baseline.
Thus the pooled right-anchor channel has a useful narrower signal, while this
complete factorized codec has no total-compression win. It does not reject all
grammar models, constructor bags, neural infilling or descendants.

The eighteen materialized weight-storage arms also completed: all 435 tensors
match, including an independent original C++ reader/dump. Best was transpose+
LZMA at 20,327,323 B versus the original 2,978,039 B. This container stores tables
that the native codec regenerates, so the loss is not evidence that every
representation-aware entropy layout must fail. A new eighteen-arm version keeps
the original dtype/storage values and exact verified RoPE regeneration, loads
the model once before fork, and schedules heavy tasks first. Its result remains
pending. All four lanes were used in the first sweep, but its recorded per-case
CPU excludes model parsing before the timer; do not derive full utilization from
that incomplete number.

Both completed notebooks' compact evidence is local:
research_round13_completed_compact_evidence_v1.zip, 75,327,948 B, SHA
1204ea8c3c9fe64da99c08265b30c51cfc0d4b5888014dd29855fd436eb7c7f6.
All 311 entry hashes and ZIP CRCs passed. The archive includes all constructor
archives, manifests, the frozen selection, all storage JSON/hash records and
the best storage container. Other storage containers remain in the private
notebook outputs and remote pulls; they are not falsely described as local.

## Submitted jobs and their exact scope

Each new notebook uses four pinned persistent process lanes and immutable,
hash-verified assets. No paid GPU or rental has been used.

| Actual notebook reference | State observed | Work |
|---|---|---|
| chaoscpp/hutter-r13-warm-development-v1 | RUNNING, 13:45 UTC | Eight 3 MiB canonical regions; native 2 MiB warmup then 1 MiB score; twelve corrected causal replay laws; independent native baseline decode |
| chaoscpp/hutter-r13-warm-confirmation-v1 | RUNNING, 13:45 UTC | Eight separate confirmation regions, same fixed laws; selection must be frozen before outcomes are opened |
| chaoscpp/hutter-r13-constructor-descendants-v1 | COMPLETE, preserved | 144 complete paid raw-text proxy cases and inverses |
| chaoscpp/hutter-r13-weight-storage-v1 | COMPLETE, preserved | Eighteen exact materialized storage layouts/codecs; none beats native |
| chaoscpp/hutter-r13-full-corpus-factorization-v1 | RUNNING, 13:45 UTC | Every original byte: 1 GB, 239 equal-boundary chunks, gzip/zstd/Markov/coarse-right, 956 actual encode/decode tasks |
| chaoscpp/hutter-r13-weight-storage-regeneration-v1 | RUNNING, 13:45 UTC | Eighteen representation-aware lossless storage arms, original dtypes and verified regeneration |
| chaoscpp/hutter-r13-native-final-head-v1 | ERROR, preserved | Failed asset verification before any compression cases: Kaggle expanded the source ZIP |
| chaoscpp/hutter-r13-native-final-head-v2 | Delivery repair launched | Same native implementation, source archive delivered as .zip.dat; four parallel native parity preflights, then four matched regional actual archive comparisons |

The full-corpus job is a complete-file reversible **raw-text proxy**. It is not
the preserved native 587,138,826-byte canonical stream, not the 99,313,750-byte
package, and not a record result. The regional native states begin at their
registered offsets and both methods receive the same warmup. They are not true
global-history snapshots. Candidate replays are not candidate archive sizes.

The native-law build uses Clang/LLD 17 and frozen portable AVX2 flags. Three lab
binaries exist: neutral 559,120 B; full residual 732,320 B; guard 732,320 B.
These raw sizes must be charged, and production packing/PGO is still unqualified.
The first live preflight timed out at 180 s on the pinned reference before any
candidate. That failed manifest remains unchanged. The committed repair instead
performs its preflight on its own four CPU lanes and gates all regional work on
neutral trajectory/archive identity and exact independent decodes.

## Audit repairs and remaining evidence gaps

All three Claude audit files were read and preserved unchanged. R12's completed
notebook archives, component timings, sources and manifests were pulled into a
separate evidence bundle. R12 A/B cancellation is recorded as the human's action;
the cancelled one-core layout is not relaunched. Two R12 fallback streams are
still running in the live session and are reused, with their legacy memory
comparisons interpreted only against the matching legacy zero-memory arm.

The following code repairs are verified:

- Memory features append to the original predictors; neutral additions match
  every original-feature prediction. The old overwriting comparison was confounded.
- WRT byte-map inversion precedes structural classification. This is a mapped
  byte class, not a complete dictionary/escape-state word decoder.
- Reset/OOV hidden rows advance decay with a zero observation and cannot reuse
  a stale activation.
- Fixed-share integer mixtures accompany the unguarded SGD laws; no exact ideal
  Bayesian regret bound is asserted for finite posterior/probability rounding.
- The old component job no longer requests invalid independent decoding of
  compression-only modes. R12's replacement is correctly labelled encode-only.
- Bootstrap intervals require at least ten independent clusters per stratum;
  eight confirmation regions are descriptive evidence below this gate.
- CLI exit zero is insufficient: every submitted resource has a verified URL.
  Initial CRLF/LF source-hash differences are recorded as transport normalization.

Thirty-seven Python properties passed after the first repairs. The added exact
regeneration/fallback test and two independent full-container framing tests also
passed. A compiled C++ check passed add-only neutrality, all-byte remapping,
deterministic positive guarded predictions and reset-row decay. Linux preflight
also checked native tensor identity and prefix causality. These are correctness
checks, not evidence of improved compression.

The earlier 9 MiB R11 live warm atlas died with its session. Its dependent word
cost and mixer work did not run; stale PIDs are no longer current authority.
The full word census did finish: 1,208,329 strict-ASCII types and 127,048,778
tokens. The 130-word constructor heuristic covers 34.8336% of tokens, not most
words. Its 16,098,886 B frequency/first-appearance table is locally preserved
with SHA a0e8824a13b84d0a911f68fd44284680b0c53aace3310134ec3175f4ea2c4c3d.
It is an offline research asset, not free inference information.

R12 measured the old cold adaptive-law gain disappearing in its early warm
prefix, and its three old-protocol BF16 finetunes lost 997/1,031/4,211 B on the
3 MiB native prefix. This is evidence against those configurations, not against
stable continuation or every warm-region residual. Its component timings put
roughly half the marginal CPU in the classical bank/mixing. The special
transformer-only mode still codes PPMD probabilities while stepping the NN;
its payload is not a pure neural-compression result.

## Resource, spending and deletion ledger

Paid spending remains $0. No models, data or other files were deleted in round
13. The optional R12 SHA-guarded cleanup proposal was inspected but not executed.
Compiler restoration added the scoped LLVM key/repository and Clang/LLD 17;
the source/key hashes and package logs are preserved in the compiler manifest.
All native source modifications are in an isolated copy; original binaries and
trees are preserved. The automatic permission review timed out on one read-only
inspection; its permitted single retry succeeded, so no user action is needed.

The managed Goal remains usageLimited; it was not resumed, replaced or bypassed.
The current manual CPU work follows the user's renewed authorization. Automated
follow-ups must honor the Goal/account limits and the 11 October research end.

## What remains before a GPU request

Preserve and independently inspect the pending native and full-corpus outputs,
including failed cases, actual archives, CPU/RSS and source hashes. Verify final
serialized full-file frames with the independent parser rather than only each
pre-serialization chunk. Freeze warm development selection before confirmation.
Promising replays require actual native archive integration and a package/time/
RAM test; no linear extrapolation from a regional reset is a qualifying result.

The 96-entry coverage report distinguishes measured finite configurations,
running mechanisms, unimplemented CPU descendants and GPU architectures.
Remaining GPU work and the $70 staged budget are in the training plan. Full
literal/OOV masking, stable original-core continuation, learned TTL/attention,
word heads and jointly trained architecture combinations remain untested.
