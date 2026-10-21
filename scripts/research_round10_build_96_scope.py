"""Finite experiment contracts for all 96 ideas; never a completion assertion."""

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
import json

P = project_root(__file__)
RECIPES = {
"representation": {
 "math": "A deterministic feature f(history) cannot add information beyond history; it can reduce approximation error or compute. Test a complete normalized residual q=(1-alpha)*q_native+alpha*q_feature with prefix-visible alpha.",
 "protocol": "Match feature dimension, stored bytes and fit targets. Compare actual glyph/letter descriptors, ordinary byte/word statistics, signed descriptor permutation and a featureless head. Fit on registered warm development clusters; score all targets, not just affected words.",
 "engineering": "Keep fonts/rendering out of deployment unless actual conditional likelihood pays their encoder/decoder code and resources. Separate an exact representation/residual codec from a predictor feature. No OCR confidence or future word may silently become side information.",
 "endpoint": "One declared symbolic descriptor family and four capacity-matched controls. Raster/CNN descendants require a separate trained architecture and paid exact residual channel.",
 "dependency": "warm native traces; a genuinely trained raster/CNN descendant needs GPU"},
"paid_factorization": {
 "math": "For an invertible X <-> (Z,Y), total length is L(Z)+L(Y|Z)+L(inverse/program). Right anchors are available only after their values and positions are decoded. An unordered set requires a paid order/subset unless the decoder reconstructs it deterministically.",
 "protocol": "Implement the transform and an independent inverse first; test identity, empty/rare/OOV/Unicode/markup edge cases and all side metadata. Compare original order, factorization with the same model capacity, and anchor-shuffled or left-only controls.",
 "engineering": "Explicit framing, length bounds, version, escaping and side-code support. Compare actual byte archives with identical assets/copy multiplicities; do not substitute a main-stream saving for total saving.",
 "endpoint": "At most three registered transform policies before development selection. One untouched confirmation pass and native full-package promotion for a positive winner.",
 "dependency": "CPU transforms; new bidirectional/infilling neural factors need GPU"},
"memory": {
 "math": "Memory M_t=F(M_{t-1},decoded x_{t-1}) is free of transmitted hints only if the decoder reconstructs it exactly. Retention horizon must be shorter than the evaluation episode, not the gradient truncation block.",
 "protocol": "Compare FIFO/recency, lexical/title retrieval and signed learned retrieval at equal memory/compute. Episodes span at least 64 KiB and, where relevant, several articles; carry state across detached BPTT blocks. Add real global-context and no-retrieval controls.",
 "engineering": "Insert only completed decoded words; use stable eviction/tie rules, tagged hashes and bounded allocations. Charge index RAM and CPU, including original native bank. Teacher-selected donors/TTL labels are paid or training-only, never free decode hints.",
 "endpoint": "One declared long-horizon memory family, three horizons and matched null controls; short-reset historical arms do not satisfy this endpoint.",
 "dependency": "warm CPU retrieval/replay; original-core learned retention requires GPU"},
"weight_codec": {
 "math": "Count exact model containers with m package copies. Fixed-code post-hoc entropy is distinct from end-to-end rate-aware quantization. For mean loss in bits, J=CE_final+m*lambda*R_model/T, lambda=1.",
 "protocol": "Neutral export must reproduce original bytes or an exactly priced format change. Compare original order/types, repaired BF16, selective precision and fixed-code entropy models; validate every native tensor, then recompress with changed rounded weights.",
 "engineering": "Use importable codecs, pinned arithmetic/count initialization/halving rules, exact RoPE regeneration and explicit dtype promotion. No FP32 optimizer noise may be mistaken for unavoidable trained-model growth.",
 "endpoint": "Three repaired old models and neutral reader/codec controls; separately register ECSQ/Pareto training. New kernel jobs implement the repaired-model archive stage.",
 "dependency": "CPU reader/archives; ECSQ or architecture retraining needs GPU"},
"word_model": {
 "math": "Normalize full word/literal/OOV support. A word law induces the unchanged code-tree probabilities by marginalizing mass over code prefixes. Spelling, morphology and semantics are approximation channels, not extra information supplied by letter algebra.",
 "protocol": "Compare independently learned word embeddings, spelling composer, positional/multiset features and a random basis with equal trainable/stored budgets and identical targets. Use root-word CE warm start followed by complete final-bit loss; record class coverage.",
 "engineering": "Exact tiled softmax or normalized conditional tree, native code-tree alignment, case/escape/length handling and literal fallback. Causal completed-word donors may modify candidates only through a normalized before-target law.",
 "endpoint": "One adequately trained representation family plus same-capacity controls, two seeds and native all-bit evaluations. Historical short frozen heads are preliminary evidence.",
 "dependency": "CPU census/tree/replay; adequate joint neural word training needs GPU"},
"native_law": {
 "math": "Predict before observing the coded bit, then update deterministic state. Optimize final-coder log loss; measure interactions I_AB=G_AB-G_A-G_B without assuming nonnegative redundancy or additive gains.",
 "protocol": "Identity, active prefix noninterference, capacity-matched generic calibration, global-context and explicit-channel ablations. Fixed learning rates 250/1000/4000 for the new integer mixer; select on first two warm windows and score last two only once.",
 "engineering": "Positive integer coding support, frozen stretch/squash assets, exact rounding/update order and independent native decode. Native trajectory replay is an intermediate stage; code/executable/RAM overhead is real.",
 "endpoint": "One registered residual/structural law and its matched controls on warm data, then actual native archives if promising. Many tiny old heads do not establish the ceiling of new architecture.",
 "dependency": "CPU native warmth; learned backbone changes require GPU"},
"training": {
 "math": "Use all-target final loss and model description, with a fixed global normalization. For sampled piece i, estimate sum_i A_i/W by mean(A_i/p_i)/W. Common/rare masks change training allocation, not the deployed entropy objective.",
 "protocol": "Unweighted continuation, soft rarity weights, full input/paid-side split and matched gradient-projection controls. Restore optimizer when possible; otherwise compare slow warmup with zero-moment controls. Full-piece useful targets, representative strata and two seeds.",
 "engineering": "BF16-grid deployment, fixed code-cell rules, exact native export, staged checkpoints and loss/rate/CPU Pareto tables. Aggregate GPU diagnostics can guide training; native checkpoint archive ranking decides compression.",
 "endpoint": "Finite 128/384/1024-step rungs with declared pruning only after useful-target and stable-control gates; surviving candidates receive native confirmation. This is not a guarantee that a short rung finds the best descendant.",
 "dependency": "GPU after CPU preparation/qualification; 5090 throughput is not yet measured"},
"runtime_and_order": {
 "math": "CPU and RAM are hard feasibility constraints. A fixed bytes-per-hour price only ranks feasible choices. Article permutation search has no general optimality guarantee; charge actual compressed permutation and inverse.",
 "protocol": "Compare unchanged production controls, coarse PPMD/NN-stepped/combined modes, and no-op transform. Article proxy fixes its winner using its declared asymmetric edge score, then reports actual paid gzip bytes; transfer to canonical native coding is a separate test.",
 "engineering": "Separate lab trace builds from uninstrumented PGO/LTO package builds. Pin affinity/compiler/source, benchmark the host, record encoder/decoder CPU and RSS separately, and preserve immutable artifacts before session replacement.",
 "endpoint": "Finite CPU component/order jobs and native production candidates; full corpus qualification needs an uninterrupted host or tested exact state serialization.",
 "dependency": "CPU session; persistent host required for complete production qualification"},
}

GROUPS = {
"representation": [1,2,3,4,5,6,9,24,30,72,73],
"paid_factorization": [8,10,11,12,26,29,38,39,56,65,85,86,87,88],
"memory": [18,19,20,21,23,25,27,28,32,33,55,57,66,71,80,81],
"weight_codec": [16,17,40,43,46],
"word_model": [13,15,64,67,68,69,70,74,75,76,77,78,79,89],
"native_law": [7,22,31,34,35,37,42,45,47,48,49,50,51,52,53,54,58,59,60,61,62,63,82,83,84],
"training": [14,36,90,91,92,96],
"runtime_and_order": [41,44,93,94,95],
}


def main():
    old = json.loads((project_path("research_round9_idea_program.json", base=P)).read_text(encoding="utf-8"))
    mapping = {f"A{number:02}": group for group, numbers in GROUPS.items() for number in numbers}
    assert len(mapping) == sum(map(len, GROUPS.values())) == 96
    entries = []
    aliases = {"core_short": "core_training_v2", "core_long": "core_extension_v1",
        "distributed_core": "core_distributed_v2", "core_selective": "core_selective_v1",
        "word_cache": "word_cache_gated_v2", "model_order": "model_order_v3",
        "core_pipeline_profile": "core_pipeline_profile_v2", "word_warmstart": "word_warmstart_v1",
        "word_softmax": "word_softmax_v1", "word_softmax_descendant": "word_softmax_v2",
        "title_memory": "title_memory_v1", "adaptive_replay": "adaptive_source_v1",
        "native_adaptive": "adaptive_native_v2", "sequence": "sequence_v1", "hidden_TTL": "hidden_sequence_v2"}
    for entry in old["entries"]:
        group = mapping[entry["id"]]
        recipe = RECIPES[group]
        evidence = []
        for captured in entry.get("round9_evidence", []):
            row = dict(captured)
            latest = project_path("research_round9_" + aliases.get(row["job"], row["job"]) + "_results.json", base=P)
            row["original_snapshot_status"] = row["status"]
            if latest.exists():
                row["status"] = json.loads(latest.read_text(encoding="utf-8-sig")).get("status", "UNKNOWN")
                row["latest_local_evidence"] = latest.name
            row["status_scope"] = "historical measured status, not current session liveness"
            evidence.append(row)
        state = "HISTORICAL_FINITE_ARMS_AND_NEW_PROTOCOL"
        if group in ["training", "word_model"] or entry["id"] in ["A03", "A24", "A83"]:
            state = "GPU_DESCENDANT_REQUIRES_IMPLEMENTATION_OR_EXECUTION"
        if entry["id"] in ["A17", "A40", "A43", "A46"]:
            state = "CPU_STORAGE_REPAIR_COMPLETE_ARCHIVES_PENDING"
        if entry["id"] in ["A31", "A42", "A62", "A63", "A82", "A84"]:
            state = "INTEGER_DESCENDANT_IMPLEMENTED_WARM_NATIVE_TEST_PENDING"
        if entry["id"] in ["A41", "A44", "A95"]:
            state = "CPU_JOB_PREPARED_OR_PRODUCTION_QUALIFICATION_PENDING"
        if not evidence and state == "HISTORICAL_FINITE_ARMS_AND_NEW_PROTOCOL":
            state = "DESCENDANT_NOT_EXECUTED"
        entries.append({"id": entry["id"], "title": entry["title"], "priority": entry["priority"],
            "recipe": group, "current_state": state, "thorough_testing_complete": False,
            "historical_evidence": entry.get("historical_evidence", {}),
            "finite_evidence": evidence, "stronger_descendant": entry["stronger_descendant"],
            "idea_specific_test": entry["discriminating_test"], "math": recipe["math"],
            "protocol": recipe["protocol"], "engineering": recipe["engineering"],
            "finite_endpoint": recipe["endpoint"], "dependencies": recipe["dependency"],
            "combination_partners": entry["combination_partners"],
            "stop_current_arm": "Stop at its predeclared finite endpoint, or a powered upper interval below actual corpus-amortized break-even. Insufficient independent data is not a negative result. Never close the entire family from a small proxy.",
            "reopen": "Reopen with a materially changed causal mechanism, newly measured warm headroom or cheaper measured deployment; register the change and matched controls first."})
    result = {"generated": datetime.datetime.now(datetime.timezone.utc).isoformat(), "entry_count": 96,
        "all96_thoroughly_tested": False, "absolute_best_descendants_established": False,
        "selection_rule": "Prioritize dependencies and measured warm final-coder opportunity. Hypothetical value-of-information probabilities or ceilings are labelled assumptions, never measured facts.",
        "current_CPU_budget": "Six prepared private jobs and two launched live-session jobs of unknown terminal status; inspect and reuse before any new launch.",
        "entries": entries}
    (project_path("research_round10_96_scope.json", base=P)).write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# All 96 ideas: finite protocols, engineering and dependencies", "This is the current experiment scope, not a claim that all tests have run. Historical evidence, best proposed descendant and the discriminating implementation are separated for every idea. Thinking hours are not reconstructed or claimed.",
             "Common promotion rule: correct causal/reversible coding; all-target normalized support; matched data/history and controls; native independent reconstruction; observed whole-package size with explicit asset copies; feasible uncontended production CPU/RAM. Conditional corpus projections require justified sampling and warmth, not just a positive cold slice."]
    for entry in entries:
        lines += [f"## {entry['id']} — {entry['title']}", f"**Current state:** {entry['current_state']}. Priority {entry['priority']}; route `{entry['recipe']}`.",
            "**Evidence actually present:** " + ("; ".join(f"{x['job']}: {x['status']}" for x in entry["finite_evidence"]) or "No round-9 execution of this descendant is recorded; historical reports describe preliminary work."),
            "**Stronger proposed descendant:** " + entry["stronger_descendant"], "**Mathematics:** " + entry["math"],
            "**Idea-specific discriminator:** " + entry["idea_specific_test"], "**Fair execution:** " + entry["protocol"],
            "**Engineering requirements:** " + entry["engineering"], "**Finite endpoint:** " + entry["finite_endpoint"],
            "**Dependencies:** " + entry["dependencies"] + ". Combination partners: " + ", ".join(entry["combination_partners"]) + ".",
            "**Stopping/reopening:** " + entry["stop_current_arm"] + " " + entry["reopen"]]
    (project_path("research_round10_96_scope.md", base=P)).write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"entries": len(entries), "all96_thoroughly_tested": False}))


if __name__ == "__main__":
    main()
