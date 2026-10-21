# CPU experiments and continuation handoff

7 October 2026. Read `research_round10_report.md` first. The latest supplied
non-GPU session is 355888412. Its Jupyter proxy returned HTTP 404 after two
workers were launched; their terminal status is unknown. A fresh CPU link has
been requested. GPU work is deliberately listed separately.

## Existing workers: inspect before any launch

| Worker | Saved manifest | PID at launch | Dependency |
|---|---|---:|---|
| Native readiness | `/kaggle/working/hp_round10/preflight_v3/manifest.json` | 121 | Original retained native binary/model/dictionary |
| Sequential warm atlas | `/kaggle/working/hp_round10/warm_atlas_v1/manifest.json` | 122 | Readiness must complete successfully |

Read manifests and process command lines after reconnect. A PID alone is not
liveness; never start a duplicate because a WebSocket timed out. Preserve a failed
manifest/log before creating a versioned repair. Root scratch may have disappeared
even when `/kaggle/working` was carried into a new session.

The atlas starts at canonical offset zero, encodes 9,437,184 bytes, warms for
1,048,576 bytes, and records sixteen later 512 KiB windows. It separately decodes
the whole prefix. Inputs include the six-byte canonical stream header, matching
the complete prepared stream rather than a silently shifted training view.
Neural/classical history is genuinely advanced. These are adjacent early-region
windows, one dependence cluster, not sixteen independent corpus samples.

Outputs: terminal manifest; encode/decode logs; actual archive and SHA; cost,
Q16, nineteen-source stage and native-hidden traces in root scratch. Each input
byte contributes 4, 16, 608 and 193 trace bytes, respectively, with a twelve-byte
stage header. Approximately 7.75 GB of trace storage is needed for this prefix;
use root scratch and preserve a compact manifest/evidence subset promptly.

## Six concrete private CPU jobs

`kaggle_cpu_round10/` contains six complete `main.py` scripts and metadata. All
are private, CPU-only, with internet disabled during execution. The local
source/model payload is `local_code_models.zip`; its current hash/size and every
entry hash are in `research_round10_private_cpu_batch_manifest.json`. They are
prepared, not submitted.

| Job | Hypothesis and exact work | Outcome/gate |
|---|---|---|
| `bf16-unweighted` | Repaired old unweighted model preserves enough likelihood after restoring BF16. Compare unchanged original and repaired model on the same sequential 3 MiB prefix, four 512 KiB windows after a 1 MiB warmup. | Actual prefix archive difference, model growth 38 B/copy, independent decode and matching within-model encode/decode trajectories. |
| `bf16-cut107_half` | Mild rare weighting remains useful after actual deployment rounding. Same paired native protocol. | Model growth 42 B/copy; score all bytes and all windows. Old unrounded archive sizes cannot be reused. |
| `bf16-cut1392_zero` | The severe mask's previous loss might change after repairing storage; reproduce rather than assume. Same paired native protocol. | Model growth 60 B/copy; common improvement cannot hide rare/OOV damage. |
| `integer-mixer` | A portable adaptive post-SSE law and carried latent summaries can improve the final law under matched warmth. Generate and independently decode one 3 MiB native baseline, then replay twelve finite arms. | Q16 identity/relabeling checks; per-window byte-equivalent gains; replay-only status until native candidate integration. |
| `component-ppmd` | CPU spent outside the strongest neural/prior path may be reallocated. Compare combined CM, PPMD alone, and PPMD with NN stepping on 256 KiB and 1 MiB sequential prefixes. | User/system/wall/RSS and actual archive sizes. The NN-stepped flag returns PPMD; this is not a pure-NN compression test. |
| `article-order-proxy` | A deterministic asymmetric similarity search may help a paid article order. Use first 512 complete raw page elements, eight fixed random controls, eight greedy starts and three directed-swap passes. Select solely on the registered edge proxy. | Gzip wrapper pays lengths/permutation, exact inverse reconstructs all original page bytes, then report actual archive size. Not a canonical native-cmix gain. |

The native jobs record actual archive hashes and copied compact archives in
`/kaggle/working/<job>/`. Inputs, models and intermediate traces remain in root
scratch; immutable input assets live in the private dataset. The archive-pair
jobs do not assume a trained model shares the baseline's hidden trajectory.
Each model's encoder and decoder must agree with each other exactly.
Exact raw reconstruction is mandatory. Check hidden-state trajectories when the
observer emits both; the retained decoder may not emit a Q16 probability trace,
so its absence is explicitly recorded rather than called a measured match.

## Mixer mathematics and controls

Its features are known before the coded bit: native Q16 log odds, optional neural
log odds/confidence, pre-SSE probability, selected classical mixture logits,
previous decoded byte class and a constant. States update after the actual bit.
Initial coefficients reproduce the native Q16 probability exactly.

The final correction preserves the original native probability at zero correction:

    q = round_Q16[p * r / (p * r + (1-p))],  r = exp(delta).

Here p is native Q16; delta is Q8 and bounded to [-8,8]; a frozen Q20 odds table
and bounded unsigned 64-bit arithmetic implement the ratio. There is no coding
libm. Coefficients use Q24 master precision so small late updates accumulate
instead of rounding to zero. The online update is a straight-through heuristic
for a discretized/clipped law, not a theorem of global convergence. Counts are
64-bit, because the corpus has more than 2^32 coded bits.

Frozen tables occupy 163,846 raw bytes. The local measured mixer state is 46,160
bytes. A long-memory bank adds 72 bytes; executable compression and total native
RSS are still to be measured. No table or option is free package information.

Registered replay arms:

- identity;
- full source law at learning-rate integers 250, 1000 and 4000;
- global context at 1000;
- removal of explicit NN feature/confidence at 1000;
- bijective context relabeling at 1000, required to match the full law exactly;
- carried hidden-summary memory at 250, 1000 and 4000;
- matched memory reset every 128 bytes at 1000;
- the same memory-feature layout with memory values zeroed at 1000.

The memory bank uses two deterministic orthogonal projections of the previously
decoded native-hidden vector and horizons 1,024, 32,768 and 131,072 completed
bytes, plus an immediate channel. Its means retain Q28 precision. Query contrast
against the most recent projection is available before the next bit. Every byte
in the 3 MiB episode advances memory; BPTT/training resets are not imposed.
This is a finite pooled-state descendant, not learned lexical eviction or a
proof that semantic retrieval is solved.

Select using the first two post-warmup windows; retain the last two as adjacent
exploratory confirmation. Do not select a new rate from their results. Save every
arm and its source hash. Native integration must keep the original predictor's
internal learning state intact and independently decode a freshly created candidate
archive. Replay gains are not actual archive byte savings.

## Upload and CLI dispatch after reconnect

1. Read and preserve the existing readiness/atlas manifests. Check corpus/model
   paths and root survival; do not replace the canonical stream with a cold fragment.
2. Upload `kaggle_cpu_round10/local_code_models.zip` as binary, not through a text
   contents endpoint. Verify its SHA against the local batch manifest. Upload
   `research_round10_private_cpu_prepare_worker.py` and the dispatcher as text.
3. Run the asset preparer once in a detached process, saving its controller log.
   It verifies full canonical SHA and the original binary/model/dictionary; takes
   a 3 MiB canonical prefix; extracts 512 complete pages for the separately labelled
   raw-page proxy; and writes `/root/hp_round10_private_assets_v1/upload/`.
   The signed session URL and CLI secret are never written into an asset.
4. Inspect `/kaggle/working/hp_round10/private_cpu_assets_manifest.json`. Its terminal
   status must be `COMPLETE_PRIVATE_CPU_ASSETS_PREPARED_NOT_UPLOADED`; preserve its
   asset ZIP hash and every entry hash locally.
5. Run the dispatcher once, detached. It reads `KAGGLE_API_TOKEN` from the runtime
   or Kaggle Secret, authenticates through the ordinary CLI, creates the private
   dataset, uses bounded readiness backoff, and submits the six scripts. It checks
   existing refs first and stops on rejection, unknown status or an account limit.
   An existing dataset is downloaded and hash-verified before reuse.
   An existing kernel is pulled and its source plus privacy/CPU/data metadata
   verified before reuse. A mismatched ref is a block, not permission to overwrite.

Underlying CLI operations are:

```text
kaggle datasets create -p /root/hp_round10_private_assets_v1/upload
kaggle kernels push -p /root/hp_round10_private_assets_v1/kernels/bf16-unweighted
kaggle kernels status chaoscpp/hutter-r10-bf16-unweighted-v1
kaggle kernels output chaoscpp/hutter-r10-bf16-unweighted-v1 -p /root/hp_round10_outputs/bf16-unweighted
```

Dataset creation is private by default; kernel metadata explicitly declares
privacy and disables GPU. See the official [dataset commands](https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets.md)
and [kernel commands](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels.md).
Never add a public flag. Actual notebook capacity is account-dependent; six
prepared scripts do not imply six accepted concurrent executions.

Preserve the dispatch manifest containing accepted refs. Poll only for material
state changes, with backoff. Download completed outputs, hash them locally, add
the terminal measurements to `results/registry.jsonl`, and update the single current
checkpoint. A push success is not execution success.

## Broader CPU experiments still pending

The six jobs are the immediate batch, not every CPU experiment in the 96-idea
portfolio. Additional dependencies and registered endpoints are explicit in
`research_round10_96_scope.md`:

- broader warm structural timestamp/title/schema/copy laws, with a generic-law
  capacity control and priced decoder-visible state;
- portable native integration of promising mixer/memory laws and separate decoder
  trajectories, followed by the uninstrumented production build;
- internal clamp/APM/mixer precision ablations, distinct from the last-Q16 bound;
- selective post-training precision/weight-codec candidates scored by native loss
  and exact container rate;
- bounded lexical retrieval, constructor-run and word-code-tree laws with full
  literal/OOV support, not target-conditioned free hints;
- canonical article-order/invertible transform integration if a proxy merits it;
- warm elasticity across retained neural checkpoints and complete resource/package
  qualification.

A full warm traversal should save only registered window traces, or maintain a
few finalist outer coders alongside one unchanged native predictor. Saving every
stage/hidden row for all T would produce hundreds of GB. That is lab instrumentation,
not a qualifying disk footprint. An online candidate must advance through unsampled
gaps; replaying only saved windows with fresh candidate state would recreate a
warmth mismatch.

The shared-state multi-coder optimization is valid only when the outer probability
correction does not alter the native predictor's internal update. Predict once,
feed each separate arithmetic coder, update each candidate after the same real
bit, then perceive that bit once in the native engine. Verify all streams against
standalone candidate execution and independently decode. It remains unimplemented.

CPU/RAM qualification requires a persistent host or verified exact state snapshots;
ordinary 12-hour notebooks cannot provide a 55–60 hour continuous traversal by
resetting at shard boundaries. No such host has been rented.

## GPU dependencies and completion rule

Stable representative original-core continuation, ECSQ, complementarity training,
adequate jointly learned word/spelling heads, long-horizon learned TTL/eviction,
adapters/distillation and content-first neural infilling remain GPU work. Their
objectives, controls, rungs, useful-target budgets and conditional 5090 hours are
in `research_round10_training_and_5090_plan.md`.

Do not mark all 96 ideas complete when the six CPU jobs finish. Close the finite
registered experiments only after their controls and evidence pass, and record
the genuinely unimplemented/dependent descendants. A corrected report, synthetic
property check or a narrow negative proxy does not finish an architecture.
Request a GPU session after the feasible CPU work, not before resolving the CPU
connection and preserving its results.

No files have been deleted in round 10. Root scratch is for intermediates, not
the sole copy of a trained model or final archive. Every future cleanup requires
verified preservation and an exact deletion manifest.
