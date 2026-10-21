"""Publish one current status after preserving historical status/report sources."""

# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
import datetime
import hashlib
import json

P = project_root(__file__)
assert (project_path("historical_reports/research_round7_checkpoint_through_20261007.md", base=P)).exists()
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
batch = json.loads((project_path("research_round10_private_cpu_batch_manifest.json", base=P)).read_text())
checkpoint = f"""# Current Hutter research checkpoint

Updated {now}. Current authority: research_round10_report.md. All older checkpoint
text is preserved in historical_reports/research_round7_checkpoint_through_20261007.md.

## Required next action

The latest supplied CPU session is 355888412. CLI authentication succeeded for
chaoscpp after the user's credential setup. The Jupyter proxy later returned HTTP
404; browser recovery also failed to initialize. No local CLI credential exists.
A fresh CPU link was requested once and is pending. No GPU session is needed yet.

Two live-session workers were launched exactly once: preflight_v3 PID 121 and
warm_atlas_v1 PID 122. Their terminal status is UNKNOWN. After reconnect, read
/kaggle/working/hp_round10/{{preflight_v3,warm_atlas_v1}}/manifest.json and process
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
  submitted. Payload {batch['payload_bytes']} bytes, SHA {batch['payload_sha256']}.
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
"""
(project_path("research_round7_checkpoint.md", base=P)).write_text(checkpoint, encoding="utf-8")
(project_path("research_round9_training_and_5090_plan.md", base=P)).write_text("""# Training-plan authority moved to round 10

The current corrected plan is [research_round10_training_and_5090_plan.md](research_round10_training_and_5090_plan.md).
It replaces the stale 85 KB export-growth argument and previous running-job claims.
The earlier plan is preserved byte-for-byte in
[historical_reports/research_round9_training_and_5090_plan_through_20261007.md](historical_reports/research_round9_training_and_5090_plan_through_20261007.md).
""", encoding="utf-8")
(project_path("research_round9_latest_measurements.md", base=P)).write_text("""# Latest measurement authority

Read [research_round10_report.md](research_round10_report.md) and the hash-indexed
[results registry](results/registry.jsonl).

Original model 2,978,039 B; new CPU BF16 repairs 2,978,077 / 2,978,081 / 2,978,099 B
(growth 38 / 42 / 60 B per copy). Four independent native readers match all 435
tensors each. Rounded-model archive results are pending.

Prior BF16-QAT native manifests: growth 23/19 B per copy; E 65,536-byte payload
savings 49/51 B. Those latest /root artifacts were lost; preserve/reproduce before
promotion. Cold G/H adaptive-law archive saving: 340 B per combined 1 MiB.
No warm full-file saving or current eligible package result is established.

The old measurement summary is preserved in
[historical_reports/research_round9_latest_measurements_through_20261007.md](historical_reports/research_round9_latest_measurements_through_20261007.md).
""", encoding="utf-8")
for name in ["research_round7_report.md", "research_round9_report.md"]:
    path = project_path(name, base=P)
    text = path.read_text(encoding="utf-8-sig")
    banner = "<!-- historical-authority-notice -->"
    if not text.startswith(banner):
        preserved = project_path("historical_reports", base=P) / (path.stem + "_through_20261007.md")
        if not preserved.exists():
            preserved.write_bytes(path.read_bytes())
        path.write_text(banner + "\n> Historical round snapshot. All status blocks and PIDs below are dated evidence. "
            "Current corrected conclusions and execution status are in [research_round10_report.md](research_round10_report.md).\n\n" + text, encoding="utf-8")
block = {"date": now, "session": 355888412, "status": "JUPYTER_PROXY_HTTP_404_FRESH_CPU_LINK_REQUESTED_ONCE",
         "live_jobs_terminal_status": "UNKNOWN", "browser_recovery": "initialization failed: kernel assets path unavailable",
         "CLI_authentication": "previously succeeded in remote runtime; no local token/config present",
         "private_jobs": "six prepared, zero submitted", "deletions": [], "paid_usd": 0}
(project_path("research_round10_connection_block.json", base=P)).write_text(json.dumps(block, indent=2), encoding="utf-8")
print(json.dumps({"published": now, "private_jobs": "PREPARED_NOT_SUBMITTED"}))
