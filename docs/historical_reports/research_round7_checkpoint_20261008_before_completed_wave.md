# Current continuation checkpoint — round 14

Updated 8 October 2026 during the active CPU research turn. Earlier checkpoint is
preserved in historical_reports/research_round7_checkpoint_through_round11_20261007.md.

Use latest human-supplied Kaggle session **356425547**; signed credential stays in
the conversation/connection environment. Kernel: 691ffb83-cd95-4964-a6f5-7101031ecafc.
Root scratch from 356326189 is gone. Inspect manifests before launching anything.
The managed Goal remains usageLimited; do not resume, replace or bypass it
automatically. Current manual work follows renewed human CPU authorization.
Research week ends 11 October. Paid spending $0; no paid rental launched.

## Verified results

- R13 actual native guard: four 3 MiB archives save 336, 286, 315 and 320 B;
  all independently decode and rebuilt neutral trajectories match pinned binary.
  Native worker CPU 139,442.213 s / 36,111.140 wall-s = 3.862 cores.
- Frozen development-selected guard saves 415.558 ideal bytes across eight
  separate 1 MiB confirmation regions after matched 2 MiB warmup. Regional
  histories are not full global history. Complete package remains unqualified.
- Full original-corpus archives: gzip 323,066,249 B; zstd 278,574,861 B;
  Markov 350,344,017 B; coarse-right 349,939,776 B. R14 independently decoded
  all four serialized archives to exactly 1 GB with original SHA
  159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc.
- Regeneration-preserving weight sweep: best 3,030,415 B, 52,376 B larger than
  original 2,978,039 B; all 435 native tensor values identical.
- All 96 ideas are NOT thoroughly exhausted. No universal impossibility,
  absolute optimum, record win or 20% full-package improvement is established.

## Current jobs and next actions

Five accepted R14 commits: constructor-development-v1, constructor-confirmation-v1,
native-confirmation-a-v1, native-confirmation-b-v1, group-weight-storage-v1,
all prefixed chaoscpp/hutter-r14-. At 13:56 UTC constructor confirmation, native B
and grouped storage were COMPLETE; two status reads hit a CLI first-import
directory race, not job failures. Collection worker rechecks all five sequentially
and pulls completed outputs to /root/r14_batch_outputs. Durable manifest:
hp_round14/batch_collection_v1.json. Do not rerun completed experiments.

Kaggle allows **five concurrent batch CPU sessions**, plus the live session.
Article-order-ppmd-v1 was initially rejected at that limit. After completed jobs
freed a normal slot, its unchanged tested source was successfully submitted at
13:58 UTC. Evidence: hp_round14/article_order_submission_v1.json. Never replay
the entire failed dispatch; its first grouped-storage job already ran.

Live full serialized verification COMPLETED before the session changed:
hp_round14/full_serialized_verification_v1.json, 956 chunks and four exact hashes.
First hard-word worker FAILED before scoring with KeyError('index'); manifests
use 'id'. Failure remains hp_round14/word_costs/manifest.json. Corrected version
runs under hp_round14/word_costs_v2/manifest.json, four lanes, restored native costs.
This failure is not evidence against words or masking.

Freeze constructor development selection before opening confirmation outcomes.
Then compare archive gains, all-target loss, actual code/model costs and CPU/RSS.
Preserve evidence locally and finish the finite CPU shortlist before asking for
a GPU session. The best possible descendant of an unrestricted family cannot
be certified by a finite sweep; distinguish tested mechanisms from open designs.

## Preservation and deletion ledger

Local compact research_round14_completed_compact_v1.zip: 21,890,661 B, SHA
b24dec333cbfdf32f622d4677fe904d497fccf1bf3247f52d11eb27d0388c90a;
156 CRC/SHA-verified entries extracted. Detailed native sources/model and two
warm-cost bundles exist under hp_round14 and are being copied locally. Check
download verification before asserting every large bundle is local.

Deleted only one redundant 75,327,948 B aggregate ZIP with a verified identical
local copy, and four 101,187,584 B duplicate decoder hidden traces whose identical
encode-side originals remain. Paths/hashes/reasons: research_round14_pull_manifest.json
and research_round14_detail_preservation.json. No original data, trained models
or unique encode-side traces were deleted.

Sources: hutter_research/, immutable kaggle_cpu_round14/sources_v1.zip and
sources_v2.zip. Keep theory separate from measured results. Round-13 audit/coverage
reports remain useful historical evidence; their RUNNING labels are stale.
