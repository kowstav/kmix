# Current Hutter research checkpoint

Updated 2026-10-07T00:35:25.599904+00:00. Current authority: research_round10_report.md. All older checkpoint
text is preserved in historical_reports/research_round7_checkpoint_through_20261007.md.

## Required next action

The latest supplied CPU session is 355888412. CLI authentication succeeded for
chaoscpp after the user's credential setup. The Jupyter proxy later returned HTTP
404; browser recovery also failed to initialize. No local CLI credential exists.
A fresh CPU link was requested once and is pending. No GPU session is needed yet.

Two live-session workers were launched exactly once: preflight_v3 PID 121 and
warm_atlas_v1 PID 122. Their terminal status is UNKNOWN. After reconnect, read
/kaggle/working/hp_round10/{preflight_v3,warm_atlas_v1}/manifest.json and process
command lines. Preserve existing outputs/root scratch before launching or repairing.
The atlas is a 9,437,184-byte sequential prefix with 1 MiB warmup and 16 later
512 KiB windows. It is one early-region cluster, not independent full-corpus strata.

## Completed locally

- Both Claude audits read completely; all 53 findings have explicit responses in
  research_round10_audit_fixes.md. Experimental repairs are not all complete.
- Original-order/BF16 old-model repairs: unweighted/mild/severe model growth
  38/42/60 bytes per copy. Neutral export reproduces original model bytes exactly.
- Independent Windows C++ reader matches all 435 tensor dtypes/shapes/bytes for
  each of four exports. New rounded models need new native archive evaluations.
- Importable codecs, integer post-SSE mixer, exact odds correction, uint64 counters,
  Q24 update precision, carried 131,072-byte hidden-summary memory and paid
  article-order proxy are implemented. 23 Python checks and C++ property tests pass.
- Six private CPU scripts/metadata and local model/source ZIP are ready, not
  submitted. Payload 9068810 bytes, SHA 91a31f266d7d1da7a1285142863156e6afd4b969a4fbbe87ada72aec74bc75e8.
  Read research_round10_pre_experiment_report.md for all commands and controls.
- README.md, results/registry.jsonl and finite protocols for all 96 ideas are the
  current index. Historical prepend-status generators are retired and preserved.

## Evidence and preservation

Canonical stream: 587,138,826 bytes, SHA
7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce.
Original model: 2,978,039 bytes, SHA
948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71.
Original corpus: 1,000,000,000 bytes, SHA
159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc.

Prior-session terminal BF16-QAT manifests show model growth 23/19 bytes and E
65,536-byte native archive gains 49/51 bytes. Their latest /root-only artifacts
were lost across session replacement; reproduce before promoting. R9 bundle 2
was locally CRC/SHA verified but predates those artifacts. Cold G/H adaptive law
archives saved 168+172 bytes per combined 1 MiB, with exact independent decode;
their warm full-file rate/package/CPU qualification is still unknown.

## Work after reconnect

1. Inspect/preserve the two already launched workers, then assemble immutable
   private assets and dispatch the six prepared CPU jobs within ordinary quotas.
2. Preserve completed CLI outputs locally and update registry/report/checkpoint.
3. Integrate promising integer/memory/structural laws into a native production
   build and independently decode. Complete warm history/package/CPU/RAM checks.
4. GPU work follows the feasible CPU stage: stable representative continuation,
   lambda=1 rate-aware training, full loss/rarity controls, adequate word and
   long-horizon learned memory architectures. Detailed conditional 5090 hours and
   $70 allocation are in research_round10_training_and_5090_plan.md.

All 96 ideas are not thoroughly tested; absolute best descendants and a 20%
whole-package improvement are not established. Paid spending remains $0.
No files were deleted in R10. Prior eleven redundant checkpoint path removals
are documented in research_round9_core_checkpoint_relocation_manifest.json.
Do not treat the surviving manifest as proof that an unpreserved model exists.

Managed Goal remains usageLimited and must not be automatically resumed,
replaced or bypassed. Automated follow-ups must honor that limit. The requested
research week ends 11 October 2026. Human steering and actual account/approval/
spending limits remain authoritative.
