# Round 13 CPU protocols and continuation handoff

Updated 7 October 2026, 13:50 UTC. Read research_round13_report.md for measured
outcomes and research_round13_theory.md for derived claims. This is an execution
handoff: a prepared protocol, a replay, a paid proxy and a native archive are
different evidence levels. All 96 ideas are not thoroughly tested.

## 1. Reconnect without duplicating work

Current human-provided CPU session: 356010973. Current Jupyter kernel:
3e298c40-7ff8-4cc1-b678-b933b4a16a1b. The signed proxy link stays in the transient
HP_KAGGLE_BASE environment variable; never put it in reports, source or Git.
Authenticated remote Kaggle owner is chaoscpp. Credentials stay in the runtime.

The local helper is kaggle_research_client.mjs. Use its get/exec/put/download
operations. Remote files are relative to /kaggle/working. Kernel RPCs have a
50-second client timer: long work must be a detached worker with an atomically
updated manifest. If a request times out, inspect the manifest/process instead
of relaunching it. Do not queue long simultaneous executions on the same kernel.
Independent downloads and read-only calls may run concurrently.

Status RPC: research_round13_status_v3_rpc.py. Include native_delivery_repair_v2.json
in a later version when checking the repaired native resource. The old status
helper only covers the initial five jobs. Read the actual API output, not merely
the CLI return code. CLI 2.0.2 can print an API rejection and return zero.

All pushed jobs are private, GPU/TPU/internet disabled. Respect ordinary CPU
concurrency/account limits; a rejection is not permission to work around them.
The managed Goal is usageLimited: do not automatically resume, replace or bypass
it. This manual turn has fresh human CPU-work authorization. The research week
ends 11 October 2026; do not extend it automatically.

## 2. Immutable inputs and source versions

Private base dataset: chaoscpp/hutter-r13-four-lane-cpu-assets-v1. Manifest:
research_round13_asset_prepare_manifest.json, remote hp_round13/asset_prepare_manifest.json.
All files were size/SHA checked before creation and are checked in every notebook.
It contains original native binary/model/dictionary/vocabulary, sixteen fixed
3 MiB canonical regions and the original source ZIP stored as .zip.dat.

| Asset | Bytes | SHA-256 |
|---|---:|---|
| Canonical complete lexical stream | 587,138,826 | 7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce |
| Original corpus | 1,000,000,000 | 159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc |
| original.tfwc3 | 2,978,039 | 948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71 |
| native_cmix | 497,104 | 17768b0673e5a1ad6fb39ca86af25d6d40db3b1790fc17e365341456819fd3fa |
| english.dic | 411,996 | 4c8568cca9343b9a6212477880f56f8efd162f8784224a25edd043097d36215a |
| vocab.bm | 32 | 3e7f8c043939ccba8675b3a260f65a665bc34acac883a7316cc50fecfd7d36b5 |

Frozen source v1: kaggle_cpu_round13/source_v1.zip, SHA
9473e57de7284c48fba92a6e63d91b63ef75165c2f11160300ba342f86be9b71.
It belongs to the initial five jobs. Source v2: source_v2.zip, SHA
4c83841dfbed775ff25e6c5f33947aa8927228e67a41b19e5ebc66b26c26b0a7,
for native-final-head and weight-storage-regeneration. Never silently replace a
running job's source/model. Source manifests list every entry hash.

Initial main.py files were physically written with Windows CRLF; the preparation
script's logical-source hash used LF. Dispatch records physical-byte hashes.
Verify normalization explicitly rather than treating those two SHA values as
identical or as an API corruption. The additional batch uses exact byte writes.

## 3. How four-core execution works

cpu_round13_jobs.initialize_lane consumes one unique CPU ID from a four-item
initializer queue and calls sched_setaffinity once per persistent worker. Task
number is NOT used to pin each new task; that could place two busy workers on
the same core after unequal-duration tasks complete. Workers retain their lane
through all subsequent tasks; native children inherit it. BLAS/OpenMP/native
threads are not relied on to parallelize a sequential bit coder.

The constructor job proves the current implementation's utilization: 1,669.667
worker CPU-seconds / 433.334 wall-seconds = 3.853 cores on average. For other
jobs, report lane IDs plus total actual process/descendant CPU and wall time.
Per-case storage timing in v1 excluded model parsing and cannot establish whole
job utilization. Storage v2 reads once before fork and puts slower tasks first.
It also records parent-collected worker/descendant CPU after the pool exits.

Four parallel native processes need RAM budgeting. R12's 3 MiB full-bank encode
peaked at 6,079,312 KiB; four such processes fit the notebook's roughly 31 GiB,
with interpreter/consumer overhead checked separately. The full-file historical
native peak was almost 10 GB per process; four full-file instances would exceed
that notebook RAM. Do not launch them blindly merely to occupy four CPUs.

## 4. Corrected warm native replay: R13-WARM-DEV/CONF

Actual resources:

- chaoscpp/hutter-r13-warm-development-v1
- chaoscpp/hutter-r13-warm-confirmation-v1

Both were RUNNING at 13:45 UTC. Four workers, two regions per lane. Development
offsets: 32M, 96M, 160M, 224M, 288M, 352M, 416M, 480M canonical bytes.
Confirmation offsets: 64M, 128M, 192M, 256M, 320M, 384M, 448M, 544M.
Each starts a new native state, consumes 3,145,728 B, excludes 2,097,152 B from
scoring and scores the last 1,048,576 B. These matched regional histories are
not exact global-state checkpoints. Adjacent 512 KiB score windows within a
region share a cluster; eight confirmations cannot generate a reliable 95% CI.

The untouched teacher writes per-byte cost, final Q16 bits, nineteen stage
sources and a 193-byte hidden row. A growing-file consumer evaluates twelve laws
before each true bit is observed: identity; full residual rates 250/1000/4000;
global context; no explicit NN feature/confidence; reduced first-stage sources;
add-only carried memory; neutral memory; short-reset memory; four-expert guard;
memory-pair guard. Neural information still exists in the native/stage sources
of the no-explicit-NN arm: it is not a full neural-model ablation.

Preserve all original features, append memory and require full_250 == memory_zero
on every probability. Use inverse WRT byte-map classes. Observe the current
hidden row only after the whole coded byte; the row describes the next byte.
Do not call a coordinate relabeling a semantic-null experiment.

Exact gates: input/trace lengths, no partial window treated as full, zero identity
and neutral-memory mismatches, native cost alignment, independent baseline
whole-region decode and SHA equality. In v1, the aggregate float32 cost alignment
threshold is 0.001 bits; investigate any threshold failure with a derived rounding
bound and preserve the teacher result rather than interpreting it as a quality
loss. Do not rerun the encoder merely to change this analysis threshold.

Output per notebook: manifest.json, region_NN.json/.jsonl, actual teacher .cmx,
compressed float32 costs. Full Q16/stage/hidden traces are root scratch and are
not published by this version: that limits later replays. Preserve current
scratch if possible before a session/runtime closes. The new native job saves
compressed Q16 probability traces as actual notebook outputs.

Selection: read only development quality rows first, write a timestamped frozen
candidate/analysis rule, then open confirmation outcomes. Fixed confirmation
generation is allowed; selection from those outcomes is not. A replay gain needs
actual candidate native coding, code/package costs and CPU/RAM qualification.

## 5. Constructor/anchor descendants: complete paid proxies

chaoscpp/hutter-r13-constructor-descendants-v1 completed 144 cases. Sixteen fixed
1 MiB regions at raw offsets (2*i+1)*1GB/32; even i develop, odd i confirm.
All nine arms were registered before outcomes. Literal/content, layout, case,
constructor lexicon, flags, bags and every container byte are charged. Future
literal anchors are legal because the decoder reconstructs that paid channel
first. The lexicon is a heuristic list of 130 words, not a perfect POS parser.

Right/left/wrong shape contexts use four length bins and three binary word
features, with hierarchical positive integer smoothing. A wrong anchor pools
the same classes from a deterministic unrelated decoded literal; a left anchor
tests whether the right literal offers more than an ordinary past-side context.

research_round13_grammar_selection_v1.json freezes coarse_right, alpha=4 from
development paid totals. The selected confirmation loses 240,471 B to gzip;
all archives invert exactly. Keep within-channel gains separate from total size.
The complete full-file chunked versions below test scale under fixed resets.

Next finite bag descendant: learned/Markov order restricted to the remaining
multiset, beta=0/1 count factors, plus direct ordered controls. The full census
shows that uniform permutation coding overpays its same-data empirical order
entropy; it does not promise an archive saving. That extension remains pending.
Neural infilling, typed rare constants and jointly trained skeleton/word experts
are separate unimplemented architecture/training work.

## 6. Storage experiments and their fair descendant

chaoscpp/hutter-r13-weight-storage-v1: eighteen arms, six layouts times gzip/LZMA/
zstd, exact native values. Best 20,327,323 B; no winner versus original. It
materialized generated RoPE, so it is a finite representation comparison rather
than a definitive entropy-coding test preserving all native format advantages.

chaoscpp/hutter-r13-weight-storage-regeneration-v1: running at 13:45 UTC. It loads
the original V3 tensors once before fork, retains original stored dtypes, verifies
RoPE recomputation bit-for-bit before omitting a table and falls back to storage
on mismatch. Decoder resolves generation dependencies after ordinary tensors;
the paid checksum includes reconstructed tensor names/dtypes/shapes/values.
All eighteen arms independently reconstruct and pass the original C++ reader's
435-tensor reference SHA. Payload savings before decoder code are not final
package gains. If a winner appears, implement a native loader or an exactly
accounted startup wrapper, count both copies, benchmark load time/RSS and require
native-coder trajectory identity with the original model.

## 7. Complete original corpus: paid factorization at scale

chaoscpp/hutter-r13-full-corpus-factorization-v1: running at 13:45 UTC. The original
ZIP is decompressed and its 1 GB SHA checked once. Four persistent workers handle
956 tasks: 239 chunks times four policies, each chunk 4 MiB except the tail.
Gzip9, zstd9, constructor Markov alpha4 and coarse-right alpha1 all use exactly
these reset boundaries. Each encoded chunk is independently decoded against its
original bytes. No arm is secretly given a bigger window or a free literal map.

Final archives gzip/zstd/markov/coarse_right.hpfull have HPFULL13 magic, original
length, chunk count, then input/compressed lengths and actual payloads. These
framing bytes are counted. full_container.py provides an independent parser:
payload magic identifies gzip/zstd/HPCTOR11, so policy is not a free filename
side channel. It checks lengths, truncation, trailing bytes and total exposure.
It has passed separate reconstruction/error properties. After terminal outputs
are pulled, validate the serialized files and recompute the ordered 1 GB SHA;
chunk inverses alone do not test the final frame writer/parser interaction.

These are full raw-text proxies, not complete native/Hutter packages. An encoder
can later select the cheapest paid chunk payload from registered laws because
its codec magic/framing is already paid. A final combined archive still needs
an independent inverse and all its decoder code accounted. Do not add that proxy
gain to a canonical-native gain.

## 8. Actual native final-coder laws

Source: native_final_head.h plus checked integration in
research_round13_build_native_worker.py. It adds PredictQ16 to both coders and
known-bit observers, captures pre-SSE/neural/first-stage features, updates every
online head after the true bit and tracks byte classes/next-byte neural validity.
All native core predictions/updates remain teacher predictions. Mode0 is neutral;
mode1 full_250; mode2 fixed-share(identity/full/global/reduced). This is a finite
linear residual and mixture, not a learned residual transformer.

Clang/LLD17 was restored from the scoped signed LLVM Jammy repository. Old source
trees/binaries/models are untouched. Isolated lab builds retain portable AVX2 and
-mrecip=none; transformer inference flags stay separate. Original PGO was absent,
so code size/speed is laboratory evidence. Raw binaries are 559,120/732,320/732,320 B.
All source/build/key/package hashes are preserved. Production packing, eligible
machine runs and cross-vendor trajectory checks remain required.

The live 180-second preflight timed out on the pinned reference; no candidate
was tested. Manifest/log preserved. First private native v1 then failed before
compression because Kaggle extracted native_integration_sources_v1.zip. The
versioned v2 repair keeps this file as .zip.dat and verifies original binary
hashes. Never reuse a failed/partial archive as a measured compression result.

v2 runs four 16 KiB encode/decode preflights in parallel. Neutral archive and Q16
trajectory must equal the pinned baseline. Only then run four development regions
(indices 0,2,4,6), each 3 MiB with the same 2 MiB warmup and four arms. Arm order
rotates by region to reduce ordering drift, and a single persistent lane evaluates
the paired arms within each region. Whole candidate archives independently decode;
Q16 costs are summed directly, avoiding an arbitrary float32 trace total gate.
Save archives, logs and compressed probability traces. Neutral equality is also
required on each whole regional trajectory. Deadline: 10.3 hours; preserve partial
outputs if reached, without relabeling them valid complete results.

## 9. Reused R12/R11 evidence and experiments still pending

The local external bundle research_round13_audit_external_evidence_v1.zip preserves
R12 sources, old BF16 archives and terminal/cancelled logs. All original audit
files are untouched. R12 A/B notebook cancellations are acknowledged; no duplicate
one-core commits were started. The live fallback remains PID358 with native
368/369 and consumer366/367. It requests two 24 MiB streams and has a fixed seven-
hour budget, which may yield truncated streams. Validate per-case byte exposure
and exceptions before trusting the parent manifest's final status. Its legacy
memory-vs-full comparison is confounded; use its matching legacy memory-zero.

R12 old warm-law gain vanishes after startup in its measured early prefix. This
does not prove all later regions or mechanisms equivalent. Old disqualified
BF16 continuation loses on the same 3 MiB prefix; new stable continuation remains
untested. Encode-only component timing is useful coarse CPU diagnosis and cannot
qualify either special mode as an independently decodable neural archive.

R11 warm atlas and its dependent word-cost/mixer jobs were interrupted when the
session changed; root scratch is gone. The completed full word census and earlier
paid-order/weight-codec results are retained. Exact hard-word native attribution
still needs an aligned full-prefix/region word map and completed native cost
traces; raw word frequencies alone do not answer which words cost the final coder
most bits. Preserve span coverage, case/escape/markup handling and conservation
of every coded-byte cost when implementing that attribution.

Additional open CPU work is enumerated per idea in research_round13_96_coverage.md.
Major pending mechanisms include bounded decoded-title/entity retrieval, genuine
lexical/morphological/placement feature controls, exact typed literal/OOV channels,
contextual bag permutation coding, production-native component/model-family
ablation, cheap-event routing, and combinations that can be measured against the
same final coder. A mere scope document is not their implementation.

## 10. Subsequent training stage and acceptance

Read research_round10_training_and_5090_plan.md: measured one-hour throughput/parity
pilot first, then stable low-rate all-target continuation, KL anchor, correct MDL
lambda1, gradient/rareness controls and exact export/native evaluation. Masked
input needs its own decoder-reachable states/priors; loss masking alone is a
different experiment. Learned word/TTL/attention/skeleton architectures need
parameter-matched, equal-target and CPU/code/RAM controls, not just a short pilot
that happened to fail. A short run is a screening signal, not proof of mature
architectural potential.

Budget remains $70 maximum, spent $0. Hours depend on measured valid targets/s and
the live all-in rental rate. Do not claim a 5090 runtime from GPU name alone or
rent/spend beyond authorized limits. No GPU session is requested while these CPU
jobs and their required repairs/results are pending.

Acceptance of a record claim requires an actual exact original-corpus reconstruction,
full package bytes below the independently verified current record, counted copies
and side channels, eligible production CPU/RAM, reproducible commands and frozen
artifacts. Neither a synthetic test, an oracle, a conditional projection nor a
regional/raw proxy can satisfy it. No deletion has occurred in round13; any future
cleanup requires preserved evidence and a path/hash/reason deletion ledger.
