# Round 10: audit repairs, CPU implementation and current evidence

7 October 2026, India time. This report is the current authority; rounds 1–9 are
historical evidence. The two Claude audits have been read completely and preserved
unchanged. Every finding has a response in `research_round10_audit_fixes.md`.

## What changed

The main correction is economic: the earlier trained-model growth was largely an
export artifact. Original tensor order and original BF16 storage remove it. New
local exports add tens of bytes, rather than roughly 85 KB, per model copy. This
reopens stable finetuning as a serious candidate; it does not establish its
full-file compression gain.

The other central corrections are to the measurement regime and decision rules:
matched sequential warmth, corpus amortization of fixed assets, all-word final
loss, aggregate GPU diagnostics rather than a per-row training veto, and explicit
CPU/RAM feasibility. Historical short cold screens remain measurements of those
screens. They cannot establish the ceilings of long-memory or word architectures.

## Completed local CPU work

Baseline model: canonical lexical `lex_h1_run11.tfwc2`, actually native format V3,
2,978,039 bytes. Baseline SHA-256 is
`948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71`.

| Export | Model bytes | Growth per model copy | Storage/native reader result |
|---|---:|---:|---|
| Neutral | 2,978,039 | 0 | Byte-identical original; all 435 tensors exact |
| Repaired old unweighted | 2,978,077 | 38 | All 435 tensors exact |
| Repaired old mild rare weighting | 2,978,081 | 42 | All 435 tensors exact |
| Repaired old severe zero weighting | 2,978,099 | 60 | All 435 tensors exact |

The repair uses round-to-nearest, ties-to-even on fields originally stored as
BF16. It preserves quantized code indices, original ordering, configuration and
the original FP32 RoPE channel. Independent Windows C++ decoding matches Python
dtype, shape and every tensor byte, including promoted BF16 values and regenerated
RoPE. These rounded models need new native encodes; old unrounded archive sizes
are not transferable. Results and exact model hashes are in
`research_round10_bf16_repair_results.json` and
`research_round10_native_reader_results.json`.

The new codec modules use normal imports rather than runtime source extraction
and `exec`. The stored adaptive-law header include and both scratch consumers
have been repaired; its standalone C++ replay builds as stored.

The new integer post-SSE mixer is implemented in `hutter_research/`. It uses
prefix-visible bit position, previous decoded byte class and optional neural
confidence, with deterministic online fixed-point updates. Its finite controls
include identity, global context and removal of the explicit neural feature and
confidence. A bijective context relabeling is an identity control, not a semantic
null. A second descendant carries projected hidden-state summaries over up to
131,072 completed bytes, with matched short-reset and zero-memory controls.
Frozen probability tables occupy 163,846 raw bytes; predictor state occupies
46,160 bytes in the measured local build, plus 72 bytes for the long-memory bank.
The observation counters are 64-bit: a global context processes more than 2^32
bits on this corpus, so a 32-bit counter would wrap. Q24 coefficient precision
prevents late small updates from rounding away, and an integer odds-ratio update
preserves the native Q16 law at zero correction. Production compressed executable size
and total RSS must still be measured.

Twenty-three Python property/unit checks pass, including existing-kernel source,
privacy and input verification. The C++ self-test passes all 65,535
neutral Q16 probabilities, 64-bit integer-square-root/counter checks, deterministic
online updates and an analytic 131,072-byte retention check. Active future-prefix mutation leaves earlier predictions unchanged;
the global-context ablation changes predictions, and context relabeling does not.
These are correctness checks, not compression-quality results.

## Measured results from the previous session

These terminal manifests survived. The latest model/archive artifacts were in
`/root` and did not survive session replacement, so these results need reproduction
before artifact-based promotion.

| Prior BF16 QAT model | Growth per copy | B archive saving | E archive saving |
|---|---:|---:|---:|
| Unweighted | 23 bytes | 68 bytes | 49 bytes |
| Half rare loss | 19 bytes | 70 bytes | 51 bytes |

Each comparison uses 65,536 canonical bytes and the actual combined CM. B
participated in fitting. E was held out from these models' continuation fitting
but was seen by other research branches. The manifests record independent
reconstruction and matching encoder/decoder neural trajectories. They do not
establish stationarity or whole-file improvement.

The frozen adaptive law's independently decoded G/H archives saved 168 and
172 bytes on two cold 512 KiB slices. This result remains valid for those slices.
Its full warm rate, portable integer descendant and complete-package result are
unmeasured. Constructor/literal splits tested so far lose after their actual side
costs. Those are finite wrapper results, not a theorem against content-first
infilling or stronger side models.

## Live-session and committed CPU status

CLI authentication succeeded for account `chaoscpp`. The user configured the
runtime secret; no credential was copied into reports, sources or datasets.
The latest supplied session is 355888412, with four vCPUs and no GPU.

Two jobs were launched once:

| Job | PID at launch | Intended measurement | Current status |
|---|---:|---|---|
| `preflight_v3` | 121 | Native 4,096-byte encode and independent decode | Unknown after connection failure |
| `warm_atlas_v1` | 122 | Sequential 9,437,184-byte prefix, 1 MiB warmup, 16 later 512 KiB windows, independent decode | Unknown after connection failure |

The Jupyter proxy subsequently returned HTTP 404. A fresh CPU-session link was
requested once. The browser recovery tool also failed to initialize because its
kernel-asset path was unavailable. No working local CLI credential is present.
The existing job manifests must be inspected before restarting anything.

Six additional private CPU scripts and their metadata are concrete and locally
compiled: three BF16 native archive pairs, an integer warm replay, a coarse CPU
component diagnostic and a paid article-order proxy. Their local source/model ZIP
has its exact size, SHA and per-entry hashes recorded in
`research_round10_private_cpu_batch_manifest.json`. **None has been submitted.** The asset builder and CLI dispatcher
are ready in the workspace; `research_round10_pre_experiment_report.md` gives
commands, data contracts, controls, expected outputs and continuation steps.

## What remains

The current 96-idea scope provides mathematical contracts, stronger proposed
descendants, matched controls, endpoints and dependencies for every idea. It
does not claim that all 96 have been thoroughly tested or that their best possible
descendants are known. Some architectures remain unimplemented; several adequate
training tests require a GPU. The repair ledger distinguishes implemented fixes
from corrected protocols and pending experiments.

The immediate sequence is: recover the CPU session; preserve/read the two existing
jobs; upload and dispatch the private CPU batch within ordinary account limits;
inspect the results; integrate promising laws into the actual native coder; then
perform complete warm package/resource qualification. Request a GPU session after
the feasible CPU stage, as instructed by the user.

A full 55–60 hour warm production run cannot be replaced by six cold notebook
segments. A persistent CPU host or tested exact state serialization is needed.
Detailed planning includes a shared-state multi-coder producer: evaluate several
outer coding laws from one unchanged native predictor traversal while maintaining
separate arithmetic-coder and candidate states. Its validity depends on keeping
the original predictor's internal update law unchanged and independently decoding
every candidate archive. This is a proposed engineering improvement, not an
implemented or measured saving.

## Size, constraints and training budget

The preserved lexical package totals 99,313,750 bytes: 92,559,456 payload plus
6,754,294 counted assets. The official reference 100,424,672 and the README's
pending 100,420,830 have separate provenance; their 3,842-byte difference is not
silently reconciled. A 20% improvement over our preserved package means a total
below 79,451,000 bytes. With unchanged assets, it
requires approximately 0.271 bits saved per canonical byte. This is a target,
not an achieved rate or forecast.

The prize counts compressor and self-extracting archive sizes, and imposes CPU,
RAM and disk constraints. GPU training does not relax CPU decoding requirements.
See the [official rules](https://hutter1.net/prize/hrules.htm). The upstream timing
and near-10-GB RSS are resource warnings requiring measurement on a qualifying
build/host; Kaggle timings cannot certify them.

The proposed $70 training allocation is in
`research_round10_training_and_5090_plan.md`. No paid compute has been rented.
Short 5090 pilots can screen finite variants, but their useful-target throughput
must be measured before quoting hours or choosing a training schedule. Neither
an absolute compression optimum nor a 20% improvement has been established.

No files were deleted during this round. The prior eleven redundant Kaggle
checkpoint paths were removed only after verified preservation; see
`research_round9_core_checkpoint_relocation_manifest.json`. All new repairs,
native-reader dumps and the source/model batch are local.
