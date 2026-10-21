"""Generate an issue-level repair ledger, with unresolved gates explicit."""

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
import re

P = project_root(__file__)

# State is deliberately narrower than 'everything fixed'. A corrected decision
# rule does not turn an unexecuted experiment into an experimental repair.
FIXES = {
"S1": ("PROTOCOL_CORRECTED", "Prioritize a payload-changing critical path and state the size target in bits per canonical byte.", "Warm native corpus evidence is still needed; tiny residual effects are not a route to the entire target."),
"S2": ("CPU_EXECUTION_BLOCKED", "A sequential warm producer was launched once; concrete private CPU jobs are prepared.", "A full 55–60 hour baseline needs a persistent host or tested exact state checkpoints; the supplied proxy is HTTP 404."),
"S3": ("PORTFOLIO_SCOPED", "Every idea now has a finite current protocol, endpoint, priority and reopening condition.", "This scopes research decisions; it does not claim thorough testing or optimal descendants for all 96 ideas."),
"S4": ("IMPLEMENTED_AWAITING_CPU", "The coarse component job records user/system CPU, wall time, RSS and actual payload per mode.", "Dedicated production build and machine benchmark remain required; a shadow price does not waive a hard limit."),
"S5": ("ENGINEERING_COMPLETE", "README, results registry and one current checkpoint replace status-block reconciliation.", "Historical files remain indexed evidence; metadata verification is not artifact reproduction."),
"M1": ("PROTOCOL_CORRECTED", "Mean bit loss uses m*lambda*R/T; lambda=1 is the size objective. The old lambda=30 conclusion is retracted.", "Stable GPU continuation and a measured Pareto frontier at lambda in {0,0.5,1,2} remain unexecuted."),
"M2": ("ENGINEERING_COMPLETE", "conditional_projection charges each fixed asset once over the declared corpus; its unit test passes.", "A rate from cold or early correlated windows is only a conditional scenario, not a stationary estimate."),
"M3": ("INFERENCE_CORRECTED", "The round-4 one-copy package conclusion remains retracted; correct two-copy totals are 21.51 versus 22.09 MB.", "No new package claim is inferred from that stand-in."),
"M4": ("PROTOCOL_CORRECTED", "Final CM and NN losses are separate outcomes; no fixed elasticity is assumed.", "Matched warm native evaluations of the same checkpoints must measure direction-dependent transfer."),
"M5": ("INFERENCE_CORRECTED", "The round-3 TTL difference was inside the stated noise band and is not an established improvement.", "Long-horizon carried-state training, repeated seeds and matched-capacity controls are GPU work."),
"M6": ("ENGINEERING_COMPLETE", "Cluster bootstrap, equivalence intervals and Holm decisions are implemented and tested.", "Current adjacent windows do not supply independent clusters; report insufficiency rather than a fabricated CI."),
"M7": ("PROTOCOL_CORRECTED", "Development must sample article types/positions independently of their measured future cost.", "The first 3–9 MiB CPU jobs are explicitly early diagnostics, not representative development strata."),
"M8": ("INFERENCE_CORRECTED", "The 64 KiB calibration confirmation cannot support rejection at an expected 1.2-byte effect.", "Size confirmation from observed cluster variance and a declared detectable effect, with package amortization."),
"M9": ("INFERENCE_CORRECTED", "The existing probability bound applies only to the last Q16 discretization.", "Internal clamp/APM/mixer precision changes require distinct native builds and independent decodes."),
"M10": ("QUALIFIED_CORRECTION", "Fixed-code entropy results do not bound a trained entropy-constrained quantizer. Lloyd-Max does not generally equalize occupancies.", "End-to-end ECSQ with actual measured container bits is GPU work; high-rate savings are not guarantees."),
"M11": ("PROTOCOL_CORRECTED", "Zero rare loss is a curriculum/specialist hypothesis; all-word final loss remains the outcome.", "Compare unweighted and soft weighting at corpus-defined thresholds with full common/rare accounting."),
"M12": ("ENGINEERING_COMPLETE", "Outcome-conditioned word classes and realized-path entropy are descriptive, not before-target compute budgets.", "Actual routing must use a prefix-visible class or a paid anchor; deploy full before-byte entropy only when available."),
"M13": ("INFERENCE_CORRECTED", "Official 100,424,672 B and README pending 100,420,830 B are labelled separate reference provenance.", "The unexplained 3,842 B difference is not silently reconciled or reused as a shared denominator."),
"D1": ("CPU_EXECUTION_BLOCKED", "Warm producer advances unchanged neural and classical state sequentially from canonical offset zero.", "Read its existing manifest after reconnect; independent full-corpus warmth and complete baseline are not finished."),
"D2": ("PROTOCOL_CORRECTED", "Both sides receive the same coding-history regime; cold-memory versus warm-core comparisons are invalidated.", "Warm native source tests and actual candidates are pending."),
"D3": ("PROTOCOL_CORRECTED", "Historical C/D/E/F and fitting prefixes are exploratory; new windows are registered before reading outputs.", "Adjacent early confirmation is still one dependence cluster; reserve independently sampled untouched corpus regions."),
"D4": ("INFERENCE_CORRECTED", "Realized-versus-expected gaps under outcome selection do not supply recoverable headroom.", "Calibration nulls bound only their finite feature/law class, not all architectures or trained mixture defects."),
"D5": ("PROTOCOL_CORRECTED", "The full original corpus was pretrained upon; fitting-held-out is not pretrained-unseen.", "Contest overfitting is legitimate if every model/data dependency is paid and decoding is exact."),
"D6": ("PROTOCOL_CORRECTED", "Select on registered development data and report confirmation once without selecting its winner.", "Reused historical test-set tuning is marked exploratory, not repaired retrospectively."),
"D7": ("CPU_QUALIFICATION_PENDING", "CPU notebook measurements are explicitly diagnostic; record affinity and contention conditions.", "Official benchmark normalization and uncontended full production resource runs remain required."),
"L1": ("PROTOCOL_CORRECTED", "Remove per-row GPU agreement as a prerequisite to attempting training; use aggregate equivalence and native checkpoint ranking.", "Native encode/decode still require exact probabilities and reconstruction; upstream aggregate fidelity does not certify our modifications."),
"L2": ("GPU_REQUIRED", "Corrected plan restores optimizer when available or uses slow warmup, full-piece targets and representative sampling.", "Old batch-1 last-256 target continuation is not a mature training test; its stable replacement has not run."),
"L3": ("ENGINEERING_COMPLETE", "BF16/original-order exports add 38, 42 and 60 B per copy; all 435 native-reader tensors match exactly. Prior BF16 QAT manifests show 23/19 B.", "New rounded models need new native archive results; the latest prior-session QAT model artifacts must be reproduced."),
"L4": ("GPU_REQUIRED", "Long-memory episodes exceed the retention horizon and carry decoder state across detached BPTT blocks.", "Short-reset negative screens do not reject long TTL; no long-horizon descendant training is complete."),
"L5": ("GPU_REQUIRED", "Train word-level representations/heads with class coverage and a full-support coding law before pricing their corpus rate.", "The frozen tiny heads and short schedules remain underpowered architectural proxies."),
"L6": ("IMPLEMENTED_AWAITING_CPU", "Integer post-SSE source mixer, genuine global-context/explicit-NN ablations and a warm replay kernel are built.", "Warm quality and native feedback/coder integration remain pending; table/executable costs are charged."),
"L7": ("PROTOCOL_CORRECTED", "Preserve original float-constant types and charge stored constants; no side channel is omitted.", "Layerwise sensitivity and selective BF16/FP32 decisions require likelihood and package measurements."),
"E1": ("ENGINEERING_PARTIAL", "New trained exports and native-reader dumps are local; six private CPU scripts persist only compact outputs with immutable assets.", "The old /root-only latest models were lost across session replacement; a manifest hash is not a preserved artifact."),
"E2": ("ENGINEERING_COMPLETE_CURRENT_CODE", "New codecs are importable modules with no runtime exec/string patching; neutral byte identity and native reader tests pass.", "Legacy sources remain historical reproductions; migrating every historical source is not claimed."),
"E3": ("ENGINEERING_COMPLETE_CURRENT_CODE", "New Python workers compile locally; new C++ predictor compiles and passes active causal/neutral/ablation tests before remote use.", "Linux end-to-end native and Kaggle runtime checks remain separate gates."),
"E4": ("CPU_QUALIFICATION_PENDING", "Lab observer/replay quality is separated from production PGO/LTO size and timing.", "The final uninstrumented build and full uncontended resource qualification have not run."),
"E5": ("ENGINEERING_PARTIAL", "Sequential warm production and dependent preflight workers are implemented and launched once.", "No complete arbitrary-state serializer exists; split cold segments cannot substitute for a full warm run."),
"E6": ("ENGINEERING_PARTIAL", "New integer coding probability law uses frozen tables, explicit rounding and pinned source/assets.", "Compiler versions and Linux/native portability comparison are pending; old libm-based law is not portable by assertion."),
"P1": ("ENGINEERING_COMPLETE", "Stored include matches stored header; scratch aliases and numeric-detail caller were updated. Standalone replay compiles locally.", "Previously preserved binary/evidence bytes remain unchanged."),
"P2": ("IMPLEMENTED_AWAITING_CPU", "New mixer probability generation and updates are integer-only; floating logarithms score diagnostics only.", "This is a new law, not a bit-identical replacement of old floating fixed-share code; native Linux quality and decode remain required."),
"P3": ("ENGINEERING_COMPLETE_CURRENT_CODE", "New codec/replay modules use normal imports and definitions rather than exec-extracted source.", "The cited old frozen-logit worker remains a historical artifact, not the current execution route."),
"P4": ("PROTOCOL_CORRECTED", "Precision/fidelity work uses FP32 native distributions or exact Q16 traces; fp16 probes cannot resolve a sub-noise KL gate.", "Old fp16 probe results retain their storage limitation."),
"P5": ("INFERENCE_CORRECTED", "The 14.86 GB datastore is outside the conservative 10 GB limit and remains excluded from deployment.", "Bounded retrieval must free memory elsewhere and measure total RSS, including the model and allocator."),
"P6": ("INFERENCE_CORRECTED", "Unchecked hash collisions in the old token-CM stand-in are identified and cannot support a production blend conclusion.", "A replacement must use tags or a documented collision estimator and native matched controls."),
"P7": ("PROTOCOL_CORRECTED", "In-sample best-lambda values are oracle diagnostics, never selected deployment gains.", "The registry keeps original raw fields but labels their evidence stage; no oracle estimate is promoted."),
"P8": ("ENGINEERING_COMPLETE_PROTOCOL", "The fixed-normalization with-replacement piece estimator replaces minibatch ratio normalization; exact expectation test passes.", "Stable full original-core training using it is GPU-dependent and not yet executed."),
"P9": ("ENGINEERING_COMPLETE", "Legacy prepend-status generators are retired; new reports/ledgers derive from explicit result and issue records.", "Old generated reports are labelled dated historical snapshots."),
"P10": ("INFERENCE_CORRECTED", "The archived field labelled 3-bit is interpreted as its actual 4-bit selector charge.", "Raw archived JSON is not silently edited; new tables use the correct bit count."),
"R1": ("ENGINEERING_COMPLETE_CURRENT_REPORTS", "New reports use normal spacing and approximately three significant figures for uncertain estimates.", "Byte counts, SHA values and trace identities retain exact precision; historical text is retained as historical."),
"R2": ("ENGINEERING_COMPLETE", "One concise current checkpoint supersedes historical append-only status; its former contents are separately preserved.", "No old PID or report header establishes current job liveness."),
"R3": ("ENGINEERING_COMPLETE_CURRENT_REPORTS", "Shared qualification limitations appear once per scope; the README links detail instead of repeating disclaimers everywhere.", "The old long ledgers remain audit evidence."),
"R4": ("ENGINEERING_COMPLETE_CURRENT_REPORTS", "Current count is 96; deletion ledger distinguishes redundant paths from model content; current CPU jobs have unknown status after HTTP 404.", "No later model is claimed locally present without an artifact check."),
"R5": ("ENGINEERING_COMPLETE_CURRENT_REPORTS", "Every results table identifies baseline, byte units, regime and asset multiplicity.", "Old FX2, lexical, ideal and actual archive values are not combined into a headline."),
}


def main():
    raw = (project_path("CLAUDE_AUDIT_01_FLAWS_REPORT.md", base=P)).read_text(encoding="utf-8-sig")
    titles = dict(re.findall(r"^### ([SMDLER]\d+)\. (.+)$", raw, re.M))
    for identifier, location, finding, severity in re.findall(r"^\| (P\d+) \| (.+?) \| (.+?) \| (.+?) \|$", raw, re.M):
        titles[identifier] = finding
    assert len(FIXES) == 53 and set(titles) == set(FIXES), (len(titles), set(titles) ^ set(FIXES))
    rows = [{"id": identifier, "finding": titles[identifier], "status": state,
             "correction": correction, "remaining_requirement": remaining}
            for identifier, (state, correction, remaining) in FIXES.items()]
    obj = {"generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "audit_sha256": hashlib.sha256((project_path("CLAUDE_AUDIT_01_FLAWS_REPORT.md", base=P)).read_bytes()).hexdigest(),
        "companion_sha256": hashlib.sha256((project_path("CLAUDE_AUDIT_02_NEXT_EXPERIMENTS_AND_THEORY.md", base=P)).read_bytes()).hexdigest(),
        "all_findings_addressed_in_ledger": True, "all_experimental_fixes_complete": False, "findings": rows}
    (project_path("research_round10_audit_fixes.json", base=P)).write_text(json.dumps(obj, indent=2), encoding="utf-8")
    lines = ["# Audit repair ledger", "Both original audit files are preserved unchanged. All 53 findings are addressed below. A corrected protocol or inference is distinguished from an executed experimental fix. GPU work, full warm qualification and the disconnected CPU jobs remain incomplete.",
             "The companion's additional mathematical corrections are derived in `research_round10_audit_response.md`; accepting an audit finding does not imply accepting its forecasts or every theorem as written."]
    for row in rows:
        lines += [f"## {row['id']}: {row['finding']}", f"**State:** {row['status']}.", row["correction"], "**Remaining:** " + row["remaining_requirement"]]
    (project_path("research_round10_audit_fixes.md", base=P)).write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"findings": len(rows), "all_experimental_fixes_complete": False}))


if __name__ == "__main__":
    main()
