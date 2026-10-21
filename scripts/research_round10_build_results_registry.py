"""Index preserved result files without upgrading their inferential status."""

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
DEST = project_path("results", base=P)
DEST.mkdir(exist_ok=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    records = []
    for path in sorted(project_glob("*_results.json", base=P)):
        try:
            obj = json.loads(path.read_text(encoding="utf-8-sig"))
        except (ValueError, UnicodeError):
            continue
        if not isinstance(obj, dict):
            continue
        identifier = path.stem.removesuffix("_results")
        protocol = project_path(identifier + "_protocol.md", base=P)
        status = obj.get("status", "NO_TOP_LEVEL_TERMINAL_STATUS")
        live = status if str(status).startswith(("COMPLETE", "FAIL")) else "HISTORICAL_SNAPSHOT_NOT_LIVENESS"
        regime = "Historical finite experiment; inspect linked protocol/data fields. No corpus-wide inference is added by indexing."
        if "bf16_repair" in identifier:
            regime = "CPU post-training original-dtype/original-order export repair; no compression evaluation"
        if "native_reader" in identifier:
            regime = "Windows native C++ storage reader versus Python reference; no model probability/archive gain"
        preservation = "Local JSON verified; inspect evidence ZIP manifests for each referenced artifact."
        if identifier in ["research_round9_native_promotion_v1", "research_round9_native_bf16_promotion_v1", "research_round9_core_bf16_qat_v1"]:
            preservation = "Terminal manifest preserved; latest /root-only model/archive artifacts lost across session replacement. Critical exports require reproduction."
        records.append({"id": identifier, "hypothesis": obj.get("scope", obj.get("purpose", "Specific finite hypothesis is documented in linked source/protocol; this index is not an independent rerun.")),
            "data": {"regime": regime, "declared_fields": {k: obj[k] for k in ["offsets", "protocol", "input_bytes", "bytes"] if k in obj}},
            "gate": "Original finite gate is historical; corrected inference/asset/warmth/CPU rules are in research_round10_audit_response.md.",
            "outcome": status, "status": live, "historical_status": status,
            "evidence": {"path": path.name, "sha256": sha(path), "bytes": path.stat().st_size},
            "protocol_path": protocol.name if protocol.exists() else None, "artifact_preservation": preservation})
    for identifier, pid, worker in [("R10-live-preflight-v3", 121, "research_round10_preflight_worker.py"),
                                    ("R10-live-warm-atlas-v1", 122, "research_round10_warm_atlas_worker.py")]:
        records.append({"id": identifier, "hypothesis": "Retained native binary/readiness and sequential warm baseline",
            "data": {"session": 355888412, "PID_at_launch": pid, "worker": worker},
            "gate": "Read existing terminal manifest after a fresh session connection; never infer completion from a launch PID.",
            "outcome": "Launched once; session proxy subsequently HTTP 404", "status": "UNKNOWN_SESSION_CONNECTION_BLOCKED",
            "evidence": {"path": worker, "sha256": sha(project_path(worker, base=P))}})
    path = project_path("research_round10_private_cpu_batch_manifest.json", base=P)
    batch = json.loads(path.read_text())
    for job in batch["jobs"]:
        records.append({"id": job["id"], "hypothesis": "Finite private CPU " + job["job"],
            "data": {"asset_dataset": batch["dataset"], "source_sha256": job["source_sha256"]},
            "gate": "Immutable asset verification, exact independent reconstruction, explicit diagnostic/production distinction",
            "outcome": "Concrete kernel sources/metadata prepared; not submitted", "status": "PREPARED_NOT_SUBMITTED",
            "evidence": {"path": job["folder"] + "/main.py", "sha256": job["source_sha256"]}})
    assert len({row["id"] for row in records}) == len(records)
    (DEST / "registry.jsonl").write_text("".join(json.dumps(row, ensure_ascii=True) + "\n" for row in records), encoding="utf-8")
    (DEST / "registry_metadata.json").write_text(json.dumps({"generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "rows": len(records), "meaning": "One indexed result-version/finite job per id. Verified local metadata, not automatic artifact reproduction or qualifying compression.",
        "registry_sha256": sha(DEST / "registry.jsonl")}, indent=2), encoding="utf-8")
    print(json.dumps({"registry_rows": len(records)}))


if __name__ == "__main__":
    main()
