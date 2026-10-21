# CPU continuation handoff

9 October 2026. Current session is 356640492; the signed credential belongs only
in the connection environment, never in committed code, reports or public files.
The newest checkpoint is research_round7_checkpoint.md. Frozen research source
bundles and private notebook outputs are the authority for reproducibility.

## Completed; do not relaunch

| Work | Actual reference or evidence | Result |
|---|---|---|
| Native guard confirmation A/B | chaoscpp/hutter-r14-native-confirmation-{a,b}-v1 | 16 actual archives, 8 paired regions, every inverse exact |
| Constructors development/confirmation | chaoscpp/hutter-r14-constructor-{development,confirmation}-v1 | 304 cases each, 608 total, selection frozen before confirmation |
| Grouped exact weight storage | chaoscpp/hutter-r14-group-weight-storage-v1 | 454 groups × 18 alternatives; 4 exact final containers; none beats original |
| Whole-file proxy reconstruction | research_round14_full_serialized_verification_v1.json | 4 serialized archives each restore the exact 1 GB corpus |
| Hard-word attribution | hp_round14/word_costs_v2/manifest.json | 16 exact native-aligned warm cost regions, all costs accounted |

Use the local extracted research_round14_batch_evidence and the verification
manifests. The initial Kaggle CLI output pull stopped at its first 500 files;
constructor jobs list 609 each. research_round14_paginated_pull_worker.py uses
the installed API's next_page_token to recover all pages. Never infer completion
from CLI exit zero, KernelWorkerStatus.COMPLETE, or the presence of a few archives.

## Native component and precision experiments

The exact registered interventions and promotion rules are in
research_round14_next_native_protocol.md. Compiled sources:
hp_round14/native_cpu_sources_v2.zip, SHA
a21f035652bf756db9e0bc43c34835ed85412540dc5dd9329d62fd1cd4183840.
Its manifest includes all 140 source entries, including the five .hpp dependencies
missed by the older archive filter. No original tree was overwritten.

The five binary names are cmix_neutral, cmix_prune_word, cmix_prune_match,
cmix_prune_indirect, cmix_output_fp32 under hp_round14/native_cpu_binaries_v2.
Read native_cpu_build_v2.json for exact flags/hashes. The neutral hash is the
same as R13; this is a useful gate, not an excuse to skip candidate decoding.

Current gate: research_round14_native_cpu_preflight_worker.py runs six 16 KiB
actual native encode/decode cases on four lanes, including pinned and neutral.
It must end PASS_NEUTRAL_PARITY_AND_SIX_EXACT_INVERSES. If it fails, inspect its
per-case logs and preserve failure; do not dispatch longer jobs or increase
timeouts blindly. The manifest is hp_round14/native_cpu_preflight_v1/manifest.json.

After this gate, research_round14_native_asset_worker.py creates one private
immutable dataset containing the five binaries, complete source and manifests.
Dataset ID is chaoscpp/hutter-r14-native-cpu-assets-v1. Verify its returned URL;
if creation is ambiguous, inspect rather than create another copy.

hutter_research/cpu_round14_native_ablation.py is the four-lane job module.
Each of four notebooks receives one arm, using the existing immutable R13 input
dataset plus the new binary dataset. It compares neutral and candidate on
regions 0,2,4,6, rotating order, 3 MiB each with 2 MiB warmup. It produces eight
archives per notebook, all independently decoded; ideal warm cost comes from
the actual coded Q16 trace, not from a separate floating predictor. Watch actual
child CPU time, not only wall progress. Do not use the compression-only special
PPMd/transformer modes for an independent inverse.

This stage answers a finite question: which complete native interventions improve
payload or buy CPU/RAM? If a pruning arm loses bits but frees resources, retain
only the measured tradeoff for a future trained combination. It cannot be called
compression progress yet. The same data cannot be recycled as untouched
confirmation; freeze survivors before using the remaining eight regions.

## Article-order repair

The original chaoscpp/hutter-r14-article-order-ppmd-v1 failed PPMd-I inverse checks
on some real regions. Several per-region tasks finished, but the entire planned
160-case result is invalid as a selection dataset until repaired. Do not select
only successful regions. The first tiny tests and canonical-prefix stress tests
passed; the real-page test failed on 3/16 combinations. Therefore preflight must
include the actual distribution and problem sizes, not just toy byte strings.

research_round14_ppmd_backend_probe_worker.py recreates three exact failures,
compares direct library calls, explicitly tests padding, and tests PPMd-H as an
alternative. It does not infer a scientific result from backend failures.
Output: hp_round14/ppmd_backend_probe_v2.json. If choosing another backend, use a
new format/version, freeze that choice before quality selection, add independent
real-data stress checks, and rerun all 160 registered cases. Pay permutation,
lengths, backend settings, payload and framing. A larger-context PPMd proxy still
does not prove transfer to the native lexical model's global history.

Sources for library API semantics are the official documentation:
https://pyppmd.readthedocs.io/en/latest/api_guide.html and
https://pyppmd.readthedocs.io/en/latest/ppmd8.html. They specify matching codec
parameters and end-of-stream behavior; they do not establish the cause of this
observed backend failure.

## Remaining CPU questions beyond this finite wave

1. Production packing/PGO and table sharing for the guard; its current code cost
   overwhelms the illustrative warm-rate gain. Verify neutral behavior after
   every optimization and include all executable copies.
2. Candidate guard × precision × resource-pruning interactions, only for survivors.
3. Full-history native confirmation on a persistent host or exact verified state
   checkpoints. A 55–60-hour baseline does not fit a 12-hour Kaggle commit.
4. Structural metadata expert ports into the lexical pipeline, with state-aware
   native WRT parsing. Earlier legacy savings are not already a lexical result.
5. Additional CPU descendants in the all-96 ledger remain explicit, including
   paid template/backoff grammar and bounded learned/symbolic feature controls.
   These have not been completed merely by running the present count models.

No finite experiment can establish the impossibility of every future descendant.
The proper endpoint is a registered implementation with honest uncertainty and
reopening criteria. Do not mark all 96 complete to satisfy a numeric checklist.

## GPU transition and budget

After collecting the finite CPU wave, freeze the shortlist and request the user's
GPU session. Start zero-step native/GPU probability and export parity before
optimization. Then run stable original-core continuation, correctly normalized
rate-aware QAT, complementarity loss, and common/rare gradient controls. Stronger
word/TTL architectures need adequate horizon and capacity controls; repeating
the old 128-step, batch-one finetunes cannot settle them.

research_round10_training_and_5090_plan.md contains the detailed staged $70 plan.
No paid machine has been ordered. Runtime estimates are throughput scenarios,
not measured 5090 requirements; benchmark useful targets/second and exact export
time in a capped pilot before allocating the balance. A CPU-only session cannot
establish actual GPU training convergence or an after-training compression rate.

## Resume safely and preserve evidence

Before launch, inspect existing manifest, notebook state and source hash. Five
concurrent committed CPU slots were observed, plus the live session. Use four
pinned independent process lanes per notebook, single-thread numerical libraries,
and avoid replaying a dispatch whose earlier pushes succeeded. Respect account,
Goal, spending and approval limits. The separate managed Goal remains usageLimited;
do not resume or replace it automatically.

The previous turn hit an approval-review usage limit. The blocked probe did not
execute. Manual work resumed only after the user returned on 9 October and a
normal review allowed access. The research week ends 11 October; no silent
extension or billing authorization is implied.

Root scratch vanishes on session replacement. Models and unique input artifacts
must remain in /kaggle/working or immutable private datasets; compact manifests,
candidate archives and sources must also be verified locally. The 200 MB working
headroom is tight: put bulky scratch in /root, preserve compact evidence, and
delete only individually verified redundant artifacts with an explicit ledger.
